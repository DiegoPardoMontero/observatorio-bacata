"""IBOCA más reciente de cada estación (RF-08): la última hora con NowCast."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gold import conexion, hora_sitio  # noqa: E402

con = conexion()
cursor = con.execute(
    f"""
    SELECT
        estacion_id,
        {hora_sitio('fecha_hora')} AS fecha_hora,
        round(pm25, 1) AS pm25,
        pm25_nowcast,
        iboca,
        iboca_nivel,
        iboca_categoria,
        iboca_color_hex
    FROM fct_aire_iboca_hora
    WHERE pm25_nowcast IS NOT NULL
    QUALIFY row_number() OVER (PARTITION BY estacion_id ORDER BY fecha_hora DESC) = 1
    """
)
columnas = [c[0] for c in cursor.description]
json.dump([dict(zip(columnas, f)) for f in cursor.fetchall()], sys.stdout, ensure_ascii=False)
