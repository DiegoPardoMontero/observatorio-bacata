"""Extractor de la RMCAB (Red de Monitoreo de Calidad del Aire de Bogotá).

Descarga el reporte horario de un día desde el portal de la Secretaría de
Ambiente y lo guarda en Bronze como Parquet, sin limpiar nada: los -9999 y los
códigos de estado quedan tal como vienen. Detalles en
docs/decisiones/0001-extraccion-rmcab.md.

Uso:
    python -m extract.rmcab --fecha 2026-09-01
    python -m extract.rmcab --desde 2026-08-01 --hasta 2026-08-31
    python -m extract.rmcab --recientes   # lo que usa el cron cada hora
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import duckdb
import httpx
import pandas as pd

URL_REPORTE = "http://rmcab.ambientebogota.gov.co/Report/HourlyReports"
USER_AGENT = (
    "ObservatorioBacata/0.1 (+https://github.com/DiegoPardoMontero/observatorio-bacata)"
)
DIR_BRONZE = Path("data/bronze/rmcab__horario")
ZONA_BOGOTA = ZoneInfo("America/Bogota")

# Cada serie (estación × monitor) es un checkbox cuyo onclick trae los datos del día:
# graph('<estación>','LineChart','EnvistaUlt.Monitor','<datos>',<catálogo>,
#       '<canal>','<unidad>','<nombre visible>','1')
_PATRON_CHECKBOX = re.compile(r'id="GraphCheck_\d+_M_\d+" onclick="([^"]*)"')
_PATRON_GRAPH = re.compile(
    r"graph\('(?P<estacion>\d+)','LineChart','[^']*','(?P<datos>\[.*?\])',"
    r"(?P<catalogo>\[.*\]),'(?P<canal>\d+)','(?P<unidad>[^']*)','[^']*','\d+'\)$",
    re.DOTALL,
)
# Códigos de estado que el portal muestra como dato válido (true) u oculta (false).
_PATRON_ESTADOS = re.compile(r"var StatusDic=(\{[^}]*\})")

COLUMNAS = [
    "estacion_codigo",
    "estacion_nombre",
    "canal",
    "parametro",
    "unidad",
    "fecha_hora_fuente",
    "valor",
    "estado",
    "estado_valido_portal",
    "fecha_reporte",
    "fecha_extraccion",
    "hash_pagina",
]


class ContratoRMCABRoto(Exception):
    """El portal respondió algo que no tiene la forma esperada."""


def descargar_dia(fecha: date, cliente: httpx.Client, intentos: int = 5) -> bytes:
    """Descarga el reporte horario de un día (todas las estaciones, unos 8 MB).

    El portal a veces responde 500 durante unos minutos y luego se recupera, así
    que se reintenta con esperas crecientes (10, 20, 40 y 80 s).
    """
    params = {"id": 1, "UserDateString": fecha.isoformat()}
    for intento in range(1, intentos + 1):
        try:
            respuesta = cliente.get(URL_REPORTE, params=params)
            respuesta.raise_for_status()
            return respuesta.content
        except (httpx.TransportError, httpx.HTTPStatusError):
            if intento == intentos:
                raise
            time.sleep(10 * 2 ** (intento - 1))
    raise AssertionError("inalcanzable")


def parsear_dia(
    pagina: str,
    fecha_reporte: date,
    fecha_extraccion: datetime | None = None,
    hash_pagina: str = "",
) -> pd.DataFrame:
    """Convierte la página de un día en filas largas: una por estación, parámetro y hora."""
    coincidencia = _PATRON_ESTADOS.search(pagina)
    if not coincidencia:
        raise ContratoRMCABRoto("no se encontró el diccionario de estados (StatusDic)")
    estados_validos = {
        int(codigo) for codigo, valido in json.loads(coincidencia.group(1)).items() if valido
    }

    onclicks = _PATRON_CHECKBOX.findall(pagina)
    if not onclicks:
        raise ContratoRMCABRoto("la página no trae ninguna serie horaria")

    # La fuente marca cada hora por su final: 01:00 es el promedio de 00:00 a 01:00
    # y la hora 24 aparece como 00:00 del día siguiente.
    primera_hora = datetime.combine(fecha_reporte, datetime.min.time()) + timedelta(hours=1)
    ultima_hora = primera_hora + timedelta(hours=23)
    fecha_extraccion = fecha_extraccion or datetime.now(timezone.utc)

    filas = []
    for onclick in onclicks:
        llamada = _PATRON_GRAPH.match(html.unescape(onclick))
        if not llamada:
            raise ContratoRMCABRoto(f"serie con formato desconocido: {onclick[:120]}")
        estacion_codigo = int(llamada["estacion"])
        canal = int(llamada["canal"])
        catalogo = json.loads(llamada["catalogo"])
        estacion_nombre = next(
            (m["stationName"] for m in catalogo if m.get("stationSerialCode") == estacion_codigo),
            None,
        )
        if estacion_nombre is None:
            raise ContratoRMCABRoto(f"estación {estacion_codigo} sin nombre en el catálogo")

        for registro in json.loads(llamada["datos"]):
            # El canal no identifica el parámetro (el 18 es PM2.5 en una estación y
            # ozono en otra): el parámetro es la llave del valor dentro del registro.
            parametros = [k for k in registro if k != "DATE_TIME" and not k.startswith("STATUS")]
            llaves_estado = [k for k in registro if k.startswith("STATUS")]
            if "DATE_TIME" not in registro or len(parametros) != 1 or len(llaves_estado) != 1:
                raise ContratoRMCABRoto(f"registro con llaves inesperadas: {sorted(registro)}")
            fecha_hora = datetime.fromisoformat(registro["DATE_TIME"])
            if not primera_hora <= fecha_hora <= ultima_hora:
                raise ContratoRMCABRoto(
                    f"el portal devolvió {registro['DATE_TIME']} al pedir {fecha_reporte}"
                )
            estado = int(registro[llaves_estado[0]])
            filas.append(
                {
                    "estacion_codigo": estacion_codigo,
                    "estacion_nombre": estacion_nombre,
                    "canal": canal,
                    "parametro": parametros[0],
                    "unidad": llamada["unidad"],
                    "fecha_hora_fuente": registro["DATE_TIME"],
                    "valor": float(registro[parametros[0]]),
                    "estado": estado,
                    "estado_valido_portal": estado in estados_validos,
                    "fecha_reporte": fecha_reporte.isoformat(),
                    "fecha_extraccion": fecha_extraccion,
                    "hash_pagina": hash_pagina,
                }
            )

    return pd.DataFrame(filas, columns=COLUMNAS)


def guardar_bronze(df: pd.DataFrame, fecha_reporte: date, fecha_carga: date, dir_base: Path) -> Path:
    """Escribe el día en data/bronze/rmcab__horario/fecha_carga=AAAA-MM-DD/<fecha_reporte>.parquet."""
    destino = dir_base / f"fecha_carga={fecha_carga.isoformat()}" / f"{fecha_reporte.isoformat()}.parquet"
    destino.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.register("dia", df)
    con.execute(
        "COPY (SELECT * REPLACE (CAST(fecha_reporte AS DATE) AS fecha_reporte) FROM dia) "
        f"TO '{destino.as_posix()}' (FORMAT parquet)"
    )
    con.close()
    return destino


def extraer(fechas: list[date], dir_base: Path = DIR_BRONZE, pausa: float = 3.0) -> list[Path]:
    """Descarga, valida y guarda cada fecha. Falla en la primera que rompa el contrato."""
    fecha_carga = datetime.now(ZONA_BOGOTA).date()
    rutas = []
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=60.0) as cliente:
        for i, fecha in enumerate(fechas):
            if i:
                time.sleep(pausa)
            contenido = descargar_dia(fecha, cliente)
            df = parsear_dia(
                contenido.decode("utf-8"),
                fecha,
                hash_pagina=hashlib.sha256(contenido).hexdigest(),
            )
            ruta = guardar_bronze(df, fecha, fecha_carga, dir_base)
            rutas.append(ruta)
            print(
                f"{fecha}: {len(df)} filas, {df['estacion_codigo'].nunique()} estaciones -> {ruta}",
                flush=True,
            )
    return rutas


def _rango(desde: date, hasta: date) -> list[date]:
    return [desde + timedelta(days=d) for d in range((hasta - desde).days + 1)]


def fechas_recientes(ahora: datetime) -> list[date]:
    """Hoy y, en la madrugada, también ayer.

    La hora de 23:00 a 24:00 se publica como 00:00 del día siguiente, así que el
    reporte de ayer se completa después de medianoche. Hasta las 4 a. m. se vuelve
    a bajar para no perder las últimas horas. Antes de la 1 a. m. el día nuevo
    todavía no tiene ninguna hora publicada, así que solo se baja ayer.
    """
    hoy = ahora.astimezone(ZONA_BOGOTA)
    ayer = hoy.date() - timedelta(days=1)
    if hoy.hour == 0:
        return [ayer]
    return [ayer, hoy.date()] if hoy.hour < 4 else [hoy.date()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae el reporte horario de la RMCAB a Bronze.")
    parser.add_argument("--fecha", type=date.fromisoformat, help="un día (por defecto, hoy en Bogotá)")
    parser.add_argument("--desde", type=date.fromisoformat, help="inicio de un rango de días")
    parser.add_argument("--hasta", type=date.fromisoformat, help="fin del rango (incluido)")
    parser.add_argument("--recientes", action="store_true", help="hoy y, antes de las 4 a. m., también ayer")
    parser.add_argument("--salida", type=Path, default=DIR_BRONZE, help="carpeta Bronze de destino")
    args = parser.parse_args()

    if args.recientes:
        if args.fecha or args.desde or args.hasta:
            parser.error("--recientes no se combina con otras fechas")
        fechas = fechas_recientes(datetime.now(timezone.utc))
    elif args.desde or args.hasta:
        if not (args.desde and args.hasta) or args.fecha:
            parser.error("usa --desde y --hasta juntos, sin --fecha")
        fechas = _rango(args.desde, args.hasta)
    else:
        fechas = [args.fecha or datetime.now(ZONA_BOGOTA).date()]
    extraer(fechas, args.salida)


if __name__ == "__main__":
    main()
