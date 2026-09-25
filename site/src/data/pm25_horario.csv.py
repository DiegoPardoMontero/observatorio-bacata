"""PM2.5 horario y NowCast de los últimos 7 días, por estación (RF-09)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gold import conexion, hora_sitio  # noqa: E402

conexion().sql(
    f"""
    SELECT estacion_id, {hora_sitio('fecha_hora')} AS fecha_hora, round(pm25, 1) AS pm25, pm25_nowcast
    FROM fct_aire_iboca_hora
    WHERE fecha_hora > (SELECT max(fecha_hora) FROM fct_aire_iboca_hora) - INTERVAL 7 DAY
    ORDER BY estacion_id, fecha_hora
    """
).df().to_csv(sys.stdout, index=False)
