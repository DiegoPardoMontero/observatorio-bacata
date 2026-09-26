-- Calendario de 2005 a 2035 con los festivos de Colombia (SPEC §8). Los festivos vienen de
-- la semilla que genera scripts/semilla_festivos.py (Ley 51 de 1983 y Ley 2578 de 2026).
with dias as (
    select cast(d as date) as fecha
    from generate_series(date '2005-01-01', date '2035-12-31', interval 1 day) as t(d)
)

select
    d.fecha,
    year(d.fecha) as anio,
    cast(date_trunc('month', d.fecha) as date) as mes,
    month(d.fecha) as mes_numero,
    day(d.fecha) as dia,
    isodow(d.fecha) as dia_semana, -- 1 = lunes
    ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'][isodow(d.fecha)] as nombre_dia,
    isodow(d.fecha) >= 6 as es_fin_de_semana,
    f.fecha is not null as es_festivo,
    f.nombre as nombre_festivo,
    isodow(d.fecha) < 6 and f.fecha is null as es_dia_habil
from dias d
left join {{ ref('festivo') }} f using (fecha)
order by d.fecha
