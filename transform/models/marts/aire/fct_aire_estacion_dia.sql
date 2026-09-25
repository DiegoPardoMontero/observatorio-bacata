-- Promedio diario por estación y contaminante. Un día tiene promedio solo si hay al
-- menos 18 horas válidas (75 %, la regla PctValid del portal).
select
    estacion_id,
    contaminante,
    unidad,
    fecha,
    count(valor) as horas_validas,
    case when count(valor) >= 18 then avg(valor) end as promedio,
    max(valor) as maximo_horario
from {{ ref('fct_aire_estacion_hora') }}
group by all
