"""Localidades, estaciones, indicadores y estado de las fuentes, para todas las páginas."""

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from _gold import conexion, hora_sitio  # noqa: E402

con = conexion()


def filas(sql: str) -> list[dict]:
    cursor = con.execute(sql)
    columnas = [c[0] for c in cursor.description]
    return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]


catalogo = {
    "construido": datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "localidades": filas("SELECT * FROM dim_localidad ORDER BY localidad_id"),
    "estaciones": filas("SELECT * EXCLUDE (sigla_sda) FROM dim_estacion ORDER BY nombre"),
    "indicadores": filas("SELECT * FROM dim_indicador"),
    "fuentes": filas(
        f"""SELECT * REPLACE ({hora_sitio('ultima_extraccion')} AS ultima_extraccion,
                              {hora_sitio('dato_mas_reciente')} AS dato_mas_reciente)
            FROM estado_fuente"""
    ),
}
json.dump(catalogo, sys.stdout, ensure_ascii=False, default=str)
