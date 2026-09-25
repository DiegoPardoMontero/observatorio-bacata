"""Lectura de Gold (data/gold/*.parquet) para los data loaders del sitio.

Cada Parquet de Gold queda como una vista con su nombre (dim_localidad,
fct_aire_iboca_hora, …). Las horas de Gold son de Bogotá sin zona horaria; al
sitio salen como "AAAA-MM-DDTHH:MM:SSZ", con la hora de Bogotá marcada como
UTC, para que el navegador las muestre igual sin importar dónde esté quien las
ve. El sitio las formatea siempre en UTC (components/formato.js).
"""

import sys
from pathlib import Path

import duckdb

GOLD = Path(__file__).resolve().parents[3] / "data" / "gold"


def conexion() -> duckdb.DuckDBPyConnection:
    archivos = sorted(GOLD.glob("*.parquet"))
    if not archivos:
        sys.exit(f"No hay Gold en {GOLD}. Corre antes: make transform")
    con = duckdb.connect()
    for archivo in archivos:
        con.execute(f"CREATE VIEW {archivo.stem} AS SELECT * FROM '{archivo.as_posix()}'")
    return con


def hora_sitio(columna: str) -> str:
    """Expresión SQL que convierte una hora de Bogotá al formato del sitio."""
    return f"strftime({columna}, '%Y-%m-%dT%H:%M:%SZ')"
