-- 18 festivos al año (19 desde 2026, Ley 2578). Cuando dos caen el mismo lunes, la fecha
-- lleva los dos nombres separados por "; ", así que se cuentan nombres y no fechas.
with por_anio as (
    select anio, sum(len(string_split(nombre_festivo, '; '))) as festivos
    from {{ ref('dim_fecha') }}
    where es_festivo
    group by anio
)

select *
from por_anio
where festivos <> case when anio >= 2026 then 19 else 18 end
