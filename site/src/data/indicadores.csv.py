"""Hecho principal: un valor por localidad, mes e indicador, con el de la ciudad (SPEC §8)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gold import conexion  # noqa: E402

conexion().sql(
    """
    SELECT
        localidad_id,
        strftime(mes, '%Y-%m-%d') AS mes,
        indicador_id,
        valor,
        valor_ciudad,
        n_observaciones,
        strftime(fecha_corte_fuente, '%Y-%m-%d') AS fecha_corte_fuente
    FROM fct_indicador_localidad_mes
    ORDER BY indicador_id, localidad_id, mes
    """
).df().to_csv(sys.stdout, index=False)
