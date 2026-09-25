"""Patrón de PM2.5 por hora del día y día de la semana, últimos 90 días, por estación (RF-10)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gold import conexion  # noqa: E402

conexion().sql(
    """
    SELECT
        estacion_id,
        isodow(fecha_hora) AS dia_semana, -- 1 = lunes
        hour(fecha_hora) AS hora,
        round(avg(pm25), 1) AS pm25,
        count(pm25) AS horas
    FROM fct_aire_iboca_hora
    WHERE fecha_hora > (SELECT max(fecha_hora) FROM fct_aire_iboca_hora) - INTERVAL 90 DAY
    GROUP BY ALL
    ORDER BY ALL
    """
).df().to_csv(sys.stdout, index=False)
