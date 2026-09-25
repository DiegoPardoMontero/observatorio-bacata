"""Promedio diario de PM2.5 en agosto de 2026 para tres estaciones de la RMCAB.

Lee Bronze (data/bronze/rmcab__horario/) y escribe un CSV por la salida estándar.
Es la prueba de la Fase 0: todavía no hay Silver ni Gold, así que las reglas de
limpieza de la ADR 0001 se aplican aquí:

- Una hora es válida si el portal la marca como válida y el valor no es -9999.
- Si el mismo día se cargó varias veces, vale la carga más reciente.
- La fuente marca cada hora por su final, así que las 24 horas de un día van de
  la 01:00 a la 00:00 del día siguiente. Por eso el día es `fecha_reporte`.
- El promedio diario solo se calcula si hay al menos 18 horas válidas (75 %,
  la regla PctValid del portal). Si no, el día queda vacío.
"""

import sys
from pathlib import Path

import duckdb
import pandas as pd

RAIZ = Path(__file__).resolve().parents[3]
BRONZE = RAIZ / "data" / "bronze" / "rmcab__horario"

# Código RMCAB -> nombre con tildes y localidad donde está la estación
ESTACIONES = {
    9: ("Kennedy", "Kennedy"),
    4: ("Tunal", "Tunjuelito"),
    1: ("Usaquén", "Usaquén"),
}

if not any(BRONZE.glob("*/*.parquet")):
    sys.exit(
        f"No hay datos en {BRONZE}. Corre antes:\n"
        "  python -m extract.rmcab --desde 2026-08-01 --hasta 2026-08-31"
    )

con = duckdb.connect()
con.register(
    "estacion",
    pd.DataFrame(
        [(codigo, nombre, localidad) for codigo, (nombre, localidad) in ESTACIONES.items()],
        columns=["codigo", "estacion", "localidad"],
    ),
)
diario = con.execute(
    f"""
    WITH horas AS (
        SELECT
            estacion_codigo,
            fecha_reporte,
            valor,
            estado_valido_portal AND valor <> -9999 AS valida,
            row_number() OVER (
                PARTITION BY estacion_codigo, fecha_hora_fuente
                ORDER BY fecha_extraccion DESC
            ) AS orden_carga
        FROM read_parquet('{BRONZE.as_posix()}/*/*.parquet')
        WHERE parametro = 'PM2.5'
          AND fecha_reporte BETWEEN DATE '2026-08-01' AND DATE '2026-08-31'
    )
    SELECT
        h.fecha_reporte AS fecha,
        e.estacion,
        e.localidad,
        count(*) FILTER (h.valida) AS horas_validas,
        CASE WHEN count(*) FILTER (h.valida) >= 18
            THEN round(avg(h.valor) FILTER (h.valida), 1)
        END AS pm25
    FROM horas h
    JOIN estacion e ON e.codigo = h.estacion_codigo
    WHERE h.orden_carga = 1
    GROUP BY ALL
    ORDER BY e.estacion, fecha
    """
).df()

if len(diario) != 31 * len(ESTACIONES):
    sys.exit(f"Se esperaban {31 * len(ESTACIONES)} filas (31 días × 3 estaciones) y hay {len(diario)}")

diario.to_csv(sys.stdout, index=False)
