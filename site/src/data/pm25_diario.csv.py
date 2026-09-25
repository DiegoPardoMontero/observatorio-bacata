"""Promedio diario de PM2.5 por estación, toda la historia (RF-09)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gold import conexion  # noqa: E402

conexion().sql(
    """
    SELECT estacion_id, strftime(fecha, '%Y-%m-%d') AS fecha, round(promedio, 1) AS pm25, horas_validas
    FROM fct_aire_estacion_dia
    WHERE contaminante = 'pm25'
    ORDER BY estacion_id, fecha
    """
).df().to_csv(sys.stdout, index=False)
