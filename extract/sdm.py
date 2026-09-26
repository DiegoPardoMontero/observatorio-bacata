"""Extractor de víctimas de siniestros viales (Secretaría Distrital de Movilidad, base SIGAT).

Baja las capas MUERTO y LESIONADO del servicio Siniestralidad_BD de la SDM: una fila por
víctima, con la localidad y el tipo de actor (peatón, ciclista, motociclista, conductor o
pasajero). Solo desde 2021: antes, la fuente duplica los formularios. Detalles en
docs/decisiones/0006-fuentes-de-movilidad.md.

La fuente conserva toda su historia y los registros se siguen digitando durante semanas,
así que Bronze guarda un archivo por año que se reemplaza en cada carga, en vez de una
copia por carga: data/bronze/sdm__victima/anio_ocurrencia=AAAA/victimas.parquet.

Solo se piden los campos necesarios: el género, la edad y la dirección de las víctimas
nunca se descargan.

Uso:
    python -m extract.sdm               # el año en curso, el anterior y los que falten en Bronze
    python -m extract.sdm --desde 2021  # todos los años desde uno hasta el actual
"""

from __future__ import annotations

import argparse
import csv
import os
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import duckdb
import httpx
import pandas as pd

URL_SERVICIO = "https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer"
USER_AGENT = "ObservatorioBacata/0.1 (+https://github.com/DiegoPardoMontero/observatorio-bacata)"
DIR_BRONZE = Path("data/bronze/sdm__victima")
SEMILLA_LOCALIDADES = Path(__file__).resolve().parents[1] / "transform" / "seeds" / "localidad.csv"
ZONA_BOGOTA = ZoneInfo("America/Bogota")
PRIMER_ANIO = 2021
PAGINA = 2000  # maxRecordCount del servicio

CAMPOS = [
    "CODIGO_ACCIDENTADO", "FORMULARIO", "FECHA_OCURRENCIA_ACC", "HORA_OCURRENCIA_ACC",
    "ANO_OCURRENCIA_ACC", "CLASE_ACC", "LOCALIDAD", "CONDICION", "CONDICION_A",
]
# Capa -> (nombre en la fuente, campos que se piden)
CAPAS = {
    0: ("MUERTO", [*CAMPOS, "MUERTE_POSTERIOR"]),
    1: ("LESIONADO", CAMPOS),
}
CONDICIONES = {"PEATON", "CICLISTA", "MOTOCICLISTA", "CONDUCTOR", "PASAJERO"}
# Nombres de la fuente que no coinciden con el canónico al quitar tildes y mayúsculas
ALIAS_LOCALIDAD = {"CANDELARIA": "LA CANDELARIA"}

COLUMNAS = [
    "codigo_accidentado", "formulario", "capa", "fecha_ocurrencia", "hora_ocurrencia",
    "clase_acc", "localidad_nombre", "localidad_codigo", "condicion", "condicion_a",
    "muerte_posterior", "fecha_extraccion",
]


class ContratoSDMRoto(Exception):
    """La fuente respondió algo que no tiene la forma esperada."""


def normalizar(nombre: str) -> str:
    """Mayúsculas y sin tildes. La Ñ también pierde la virgulilla: 'NARIÑO' -> 'NARINO'."""
    sin_tildes = unicodedata.normalize("NFD", nombre.upper())
    return " ".join("".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").split())


def codigos_localidad(semilla: Path = SEMILLA_LOCALIDADES) -> dict[str, str]:
    """Nombre normalizado -> código oficial de dos dígitos, desde la semilla de dbt."""
    with semilla.open(encoding="utf-8") as archivo:
        return {normalizar(f["nombre"]): f["localidad_id"] for f in csv.DictReader(archivo)}


def _consultar(cliente: httpx.Client, capa: int, parametros: dict, intentos: int = 5) -> dict:
    """Consulta una capa con reintentos (10, 20, 40 y 80 s). ArcGIS responde 200 con un
    objeto "error" cuando falla, así que eso también se reintenta."""
    for intento in range(1, intentos + 1):
        try:
            respuesta = cliente.get(f"{URL_SERVICIO}/{capa}/query", params={**parametros, "f": "json"})
            respuesta.raise_for_status()
            datos = respuesta.json()
            if "error" in datos:
                raise httpx.HTTPStatusError(str(datos["error"]), request=respuesta.request, response=respuesta)
            return datos
        except (httpx.TransportError, httpx.HTTPStatusError, ValueError):
            if intento == intentos:
                raise
            time.sleep(10 * 2 ** (intento - 1))
    raise AssertionError("inalcanzable")


def parsear(respuesta: dict, capa: int, anio: int, codigos: dict[str, str], fecha_extraccion: datetime) -> pd.DataFrame:
    """Convierte una página de la consulta en filas de Bronze, o rompe el contrato."""
    nombre_capa, campos = CAPAS[capa]
    if "features" not in respuesta or "fields" not in respuesta:
        raise ContratoSDMRoto(f"{nombre_capa}: la respuesta no trae features ni fields")
    recibidos = [f["name"] for f in respuesta["fields"]]
    if set(recibidos) != set(campos):
        raise ContratoSDMRoto(f"{nombre_capa}: campos inesperados {sorted(set(recibidos) ^ set(campos))}")

    filas = []
    for feature in respuesta["features"]:
        a = feature["attributes"]
        if set(a) != set(campos):
            raise ContratoSDMRoto(f"{nombre_capa}: un registro trae otros campos {sorted(set(a) ^ set(campos))}")
        # Medianoche UTC del día local: se lee en UTC y se guarda como fecha, sin convertir
        fecha = datetime.fromtimestamp(a["FECHA_OCURRENCIA_ACC"] / 1000, timezone.utc).date()
        if fecha.year != anio or int(a["ANO_OCURRENCIA_ACC"]) != anio:
            raise ContratoSDMRoto(f"{nombre_capa}: víctima {a['CODIGO_ACCIDENTADO']} del {fecha}, se pidió {anio}")
        localidad = a["LOCALIDAD"]
        codigo = codigos.get(normalizar(ALIAS_LOCALIDAD.get(localidad, localidad or "")))
        if codigo is None:
            raise ContratoSDMRoto(f"{nombre_capa}: localidad desconocida {localidad!r}")
        if a["CONDICION"] not in CONDICIONES:
            raise ContratoSDMRoto(f"{nombre_capa}: tipo de actor desconocido {a['CONDICION']!r}")
        filas.append({
            "codigo_accidentado": a["CODIGO_ACCIDENTADO"],
            "formulario": a["FORMULARIO"],
            "capa": nombre_capa,
            "fecha_ocurrencia": fecha,
            "hora_ocurrencia": a["HORA_OCURRENCIA_ACC"],
            "clase_acc": a["CLASE_ACC"],
            "localidad_nombre": localidad,
            "localidad_codigo": codigo,
            "condicion": a["CONDICION"],
            "condicion_a": a["CONDICION_A"],
            "muerte_posterior": a.get("MUERTE_POSTERIOR"),
            "fecha_extraccion": fecha_extraccion,
        })
    return pd.DataFrame(filas, columns=COLUMNAS)


def extraer_anio(cliente: httpx.Client, anio: int, codigos: dict[str, str]) -> pd.DataFrame:
    """Todas las víctimas de un año, de las dos capas, página por página."""
    fecha_extraccion = datetime.now(timezone.utc)
    partes = []
    for capa, (nombre_capa, campos) in CAPAS.items():
        filtro = {"where": f"ANO_OCURRENCIA_ACC={anio}"}
        esperadas = _consultar(cliente, capa, {**filtro, "returnCountOnly": "true"})["count"]
        paginas, desde = [], 0
        while True:
            respuesta = _consultar(cliente, capa, {
                **filtro, "outFields": ",".join(campos), "returnGeometry": "false",
                "orderByFields": "OBJECTID", "resultOffset": desde, "resultRecordCount": PAGINA,
            })
            pagina = parsear(respuesta, capa, anio, codigos, fecha_extraccion)
            paginas.append(pagina)
            desde += len(pagina)
            if len(pagina) == 0 or not respuesta.get("exceededTransferLimit"):
                break
        capa_df = pd.concat(paginas, ignore_index=True)
        if len(capa_df) != esperadas:
            raise ContratoSDMRoto(f"{nombre_capa} {anio}: se bajaron {len(capa_df)} filas y el servidor cuenta {esperadas}")
        partes.append(capa_df)
    df = pd.concat(partes, ignore_index=True)
    repetidos = df["codigo_accidentado"][df["codigo_accidentado"].duplicated()]
    if not repetidos.empty:
        raise ContratoSDMRoto(f"{anio}: códigos de víctima repetidos, por ejemplo {repetidos.iloc[0]}")
    return df


def guardar_bronze(df: pd.DataFrame, anio: int, dir_base: Path) -> Path:
    """Reemplaza el archivo del año. Se escribe aparte y se renombra, para no dejarlo a medias."""
    destino = dir_base / f"anio_ocurrencia={anio}" / "victimas.parquet"
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".parquet.tmp")
    con = duckdb.connect()
    con.register("victimas", df)
    con.execute(f"COPY (SELECT * FROM victimas ORDER BY codigo_accidentado) TO '{temporal.as_posix()}' (FORMAT parquet)")
    con.close()
    os.replace(temporal, destino)
    return destino


def anios_a_bajar(actual: int, desde: int | None, dir_base: Path) -> list[int]:
    """Con --desde, todos los años desde ese. Si no, el año en curso y el anterior (los que se
    siguen digitando) y cualquier año desde 2021 que falte en Bronze: así la primera corrida
    en CI, o en un clon nuevo, completa la historia sola."""
    if desde is not None:
        return list(range(max(PRIMER_ANIO, desde), actual + 1))
    return [
        anio for anio in range(PRIMER_ANIO, actual + 1)
        if anio >= actual - 1 or not (dir_base / f"anio_ocurrencia={anio}" / "victimas.parquet").exists()
    ]


def extraer(desde: int | None = None, dir_base: Path = DIR_BRONZE) -> list[Path]:
    actual = datetime.now(ZONA_BOGOTA).year
    codigos = codigos_localidad()
    rutas = []
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=120.0) as cliente:
        for anio in anios_a_bajar(actual, desde, dir_base):
            df = extraer_anio(cliente, anio, codigos)
            ruta = guardar_bronze(df, anio, dir_base)
            rutas.append(ruta)
            muertos = int((df["capa"] == "MUERTO").sum())
            print(f"{anio}: {len(df)} víctimas ({muertos} muertos, hasta el {df['fecha_ocurrencia'].max()}) -> {ruta}")
    return rutas


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae las víctimas de siniestros viales (SDM, SIGAT) a Bronze.")
    parser.add_argument("--desde", type=int, help=f"primer año (mínimo {PRIMER_ANIO}); por defecto, el anterior y los que falten")
    parser.add_argument("--salida", type=Path, default=DIR_BRONZE, help="carpeta Bronze de destino")
    args = parser.parse_args()
    extraer(args.desde, args.salida)


if __name__ == "__main__":
    main()
