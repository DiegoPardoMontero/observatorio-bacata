"""Extractor de Delito de Alto Impacto (Secretaría de Seguridad, SDSCJ).

Descarga los GeoJSON del dataset en Datos Abiertos Bogotá y los guarda en Bronze
como Parquet, sin limpiar nada. Cada archivo es un acumulado del año a la fecha
por localidad: "Ene-Ago (2025vs2026)" trae, para cada año desde 2018, los delitos
de enero a agosto. No es una serie mensual. Detalles en
docs/decisiones/0002-extraccion-delito-alto-impacto.md.

Uso:
    python -m extract.sdscj
"""

from __future__ import annotations

import argparse
import calendar
import hashlib
import io
import json
import re
import time
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import duckdb
import httpx
import pandas as pd

URL_DATASET = (
    "https://datosabiertos.bogota.gov.co/api/3/action/package_show"
    "?id=delito-de-alto-impacto-bogota-d-c"
)
USER_AGENT = (
    "ObservatorioBacata/0.1 (+https://github.com/DiegoPardoMontero/observatorio-bacata)"
)
DIR_BRONZE = Path("data/bronze/sdscj__delito_alto_impacto")
ZONA_BOGOTA = ZoneInfo("America/Bogota")

# Códigos de delito en los nombres de campo. Los nombres vienen de los alias del
# servicio REST de la SDSCJ (oaiee.scj.gov.co, capa 0 de CifrasSCJ).
DELITOS = {
    "H": "Homicidios",
    "LP": "Lesiones personales",
    "HP": "Hurto a personas",
    "HR": "Hurto a residencias",
    "HA": "Hurto de automotores",
    "HB": "Hurto de bicicletas",
    "HC": "Hurto a comercio",
    "HCE": "Hurto de celulares",
    "HM": "Hurto de motocicletas",
    "DS": "Delitos sexuales",
    "VI": "Violencia intrafamiliar",
}
LOCALIDADES = {f"{n:02d}" for n in range(1, 21)} | {"99"}  # 99 = "Sin Localización"
PRIMER_ANIO = 2018
CAMPOS_NO_MEDIDA = {"CMIULOCAL", "CMNOMLOCAL", "CMMES", "SHAPE_AREA", "SHAPE_LEN"}

# CMH26CONT = homicidios de 2026. El GeoJSON sale de un shapefile, que corta los
# nombres a 10 caracteres: CMHCE26CONT llega como CMHCE26CON.
_PATRON_CONTEO = re.compile(r"CM(?P<delito>[A-Z]+?)(?P<anio>\d{2})CONT?")
# Variación porcentual frente al año anterior y total de la ciudad en el año actual.
_PATRON_VARIACION = re.compile(r"CM(?P<delito>[A-Z]+)VAR")
_PATRON_TOTAL = re.compile(r"CM(?P<delito>[A-Z]+)TOTAL")
# "Ene-Ago (2025vs2026)": de enero a agosto, 2026 frente a 2025.
_PATRON_PERIODO = re.compile(r"Ene-(?P<mes>[A-Z][a-z]{2}) \((?P<anterior>\d{4})vs(?P<actual>\d{4})\)")
_MESES = {m: i for i, m in enumerate(
    ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"], start=1
)}

COLUMNAS = [
    "localidad_codigo",
    "localidad_nombre",
    "periodo_fuente",
    "fecha_corte",
    "campo",
    "medida",
    "delito_codigo",
    "anio",
    "valor",
    "recurso_id",
    "recurso_nombre",
    "recurso_modificado",
    "fecha_extraccion",
    "hash_archivo",
]


class ContratoSDSCJRoto(Exception):
    """La fuente respondió algo que no tiene la forma esperada."""


def _get(url: str, cliente: httpx.Client, intentos: int = 5) -> httpx.Response:
    """GET con reintentos y esperas crecientes (10, 20, 40 y 80 s)."""
    for intento in range(1, intentos + 1):
        try:
            respuesta = cliente.get(url, follow_redirects=True)
            respuesta.raise_for_status()
            return respuesta
        except (httpx.TransportError, httpx.HTTPStatusError):
            if intento == intentos:
                raise
            time.sleep(10 * 2 ** (intento - 1))
    raise AssertionError("inalcanzable")


def listar_recursos(cliente: httpx.Client) -> list[dict]:
    """Recursos GeoJSON del dataset: hoy son dos, el acumulado del año en curso y el del año anterior completo."""
    paquete = _get(URL_DATASET, cliente).json()["result"]
    recursos = [r for r in paquete["resources"] if r.get("format", "").lower() == "geojson"]
    if not recursos:
        raise ContratoSDSCJRoto("el dataset no tiene recursos GeoJSON")
    return recursos


def leer_geojson(contenido_zip: bytes) -> dict:
    """Cada recurso es un .zip con un único .geojson adentro."""
    with zipfile.ZipFile(io.BytesIO(contenido_zip)) as archivo:
        nombres = [n for n in archivo.namelist() if n.lower().endswith(".geojson")]
        if len(nombres) != 1:
            raise ContratoSDSCJRoto(f"se esperaba un .geojson en el zip y hay {nombres}")
        return json.loads(archivo.read(nombres[0]))


def fecha_corte(periodo: str) -> date:
    """"Ene-Ago (2025vs2026)" -> 2026-08-31, último día del mes que cierra el acumulado."""
    coincidencia = _PATRON_PERIODO.fullmatch(periodo)
    if not coincidencia or coincidencia["mes"] not in _MESES:
        raise ContratoSDSCJRoto(f"periodo desconocido: {periodo!r}")
    anio = int(coincidencia["actual"])
    if int(coincidencia["anterior"]) != anio - 1:
        raise ContratoSDSCJRoto(f"el periodo no compara años seguidos: {periodo!r}")
    mes = _MESES[coincidencia["mes"]]
    return date(anio, mes, calendar.monthrange(anio, mes)[1])


def _clasificar(campo: str) -> tuple[str, str, int | None]:
    """Devuelve (medida, delito, año) de un nombre de campo, o rompe el contrato."""
    if m := _PATRON_CONTEO.fullmatch(campo):
        medida, anio = "conteo", 2000 + int(m["anio"])
    elif m := _PATRON_VARIACION.fullmatch(campo):
        medida, anio = "variacion_pct", None
    elif m := _PATRON_TOTAL.fullmatch(campo):
        medida, anio = "total_ciudad", None
    else:
        raise ContratoSDSCJRoto(f"campo desconocido: {campo}")
    if m["delito"] not in DELITOS:
        raise ContratoSDSCJRoto(f"delito desconocido en el campo {campo}")
    return medida, m["delito"], anio


def parsear(
    geojson: dict,
    recurso: dict | None = None,
    fecha_extraccion: datetime | None = None,
    hash_archivo: str = "",
) -> pd.DataFrame:
    """Convierte el GeoJSON en filas largas: una por localidad y campo numérico.

    La geometría se descarta: los polígonos oficiales vienen del dataset de
    localidades de Planeación, no de este.
    """
    recurso = recurso or {}
    fecha_extraccion = fecha_extraccion or datetime.now(timezone.utc)
    atributos = [f["properties"] for f in geojson.get("features", [])]

    codigos = [a.get("CMIULOCAL") for a in atributos]
    if sorted(codigos) != sorted(LOCALIDADES):
        raise ContratoSDSCJRoto(f"localidades inesperadas: {sorted(map(str, codigos))}")
    periodos = {a.get("CMMES") for a in atributos}
    if len(periodos) != 1:
        raise ContratoSDSCJRoto(f"el archivo mezcla periodos: {periodos}")
    periodo = periodos.pop()
    corte = fecha_corte(periodo)

    filas = []
    for atributo in atributos:
        for campo, valor in atributo.items():
            if campo in CAMPOS_NO_MEDIDA:
                continue
            medida, delito, anio = _clasificar(campo)
            if valor is not None and not isinstance(valor, (int, float)):
                raise ContratoSDSCJRoto(f"valor no numérico en {campo}: {valor!r}")
            filas.append(
                {
                    "localidad_codigo": atributo["CMIULOCAL"],
                    "localidad_nombre": atributo["CMNOMLOCAL"],
                    "periodo_fuente": periodo,
                    "fecha_corte": corte,
                    "campo": campo,
                    "medida": medida,
                    "delito_codigo": delito,
                    "anio": anio,
                    "valor": None if valor is None else float(valor),
                    "recurso_id": recurso.get("id"),
                    "recurso_nombre": recurso.get("name"),
                    "recurso_modificado": recurso.get("last_modified"),
                    "fecha_extraccion": fecha_extraccion,
                    "hash_archivo": hash_archivo,
                }
            )
    df = pd.DataFrame(filas, columns=COLUMNAS).astype({"anio": "Int64", "valor": "Float64"})

    # Cada localidad y delito debe traer un conteo por año, desde 2018 hasta el año del corte.
    esperados = set(range(PRIMER_ANIO, corte.year + 1))
    conteos = df[df["medida"] == "conteo"]
    if conteos.duplicated(["localidad_codigo", "delito_codigo", "anio"]).any():
        raise ContratoSDSCJRoto("hay más de un conteo para la misma localidad, delito y año")
    for localidad in sorted(LOCALIDADES):
        for delito in DELITOS:
            anios = set(
                conteos.loc[
                    (conteos["localidad_codigo"] == localidad) & (conteos["delito_codigo"] == delito),
                    "anio",
                ]
            )
            if anios != esperados:
                raise ContratoSDSCJRoto(
                    f"localidad {localidad}, {delito}: años {sorted(anios)}, "
                    f"se esperaban {PRIMER_ANIO}-{corte.year}"
                )
    return df


def guardar_bronze(df: pd.DataFrame, fecha_carga: date, dir_base: Path) -> Path:
    """Escribe data/bronze/sdscj__delito_alto_impacto/fecha_carga=AAAA-MM-DD/<fecha_corte>.parquet."""
    corte = df["fecha_corte"].iloc[0]
    destino = dir_base / f"fecha_carga={fecha_carga.isoformat()}" / f"{corte.isoformat()}.parquet"
    destino.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.register("recurso", df)
    con.execute(f"COPY recurso TO '{destino.as_posix()}' (FORMAT parquet)")
    con.close()
    return destino


def ya_guardado(hash_archivo: str, dir_base: Path) -> bool:
    """Si ese mismo archivo ya está en Bronze, en cualquier fecha de carga."""
    archivos = list(dir_base.glob("*/*.parquet"))
    if not archivos:
        return False
    rutas = ", ".join(f"'{a.as_posix()}'" for a in archivos)
    (n,) = duckdb.sql(
        f"SELECT count(*) FROM read_parquet([{rutas}]) WHERE hash_archivo = ?", params=[hash_archivo]
    ).fetchone()
    return n > 0


def extraer(dir_base: Path = DIR_BRONZE) -> list[Path]:
    """Descarga, valida y guarda cada recurso GeoJSON. Falla en el primero que rompa el contrato.

    Si un recurso no cambió desde la última carga (mismo hash), no se guarda otra copia:
    el cron corre a diario y la fuente cambia una vez al mes (SPEC §7).
    """
    fecha_carga = datetime.now(ZONA_BOGOTA).date()
    rutas = []
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=120.0) as cliente:
        for recurso in listar_recursos(cliente):
            contenido = _get(recurso["url"], cliente).content
            hash_archivo = hashlib.sha256(contenido).hexdigest()
            if ya_guardado(hash_archivo, dir_base):
                print(f"{recurso['name']}: sin cambios, no se guarda")
                continue
            df = parsear(leer_geojson(contenido), recurso, hash_archivo=hash_archivo)
            ruta = guardar_bronze(df, fecha_carga, dir_base)
            rutas.append(ruta)
            print(f"{df['periodo_fuente'].iloc[0]}: {len(df)} filas -> {ruta}")
    return rutas


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae Delito de Alto Impacto a Bronze.")
    parser.add_argument("--salida", type=Path, default=DIR_BRONZE, help="carpeta Bronze de destino")
    args = parser.parse_args()
    extraer(args.salida)


if __name__ == "__main__":
    main()
