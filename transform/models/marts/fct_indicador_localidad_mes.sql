-- Hecho principal (SPEC §8): un valor por localidad, mes e indicador, con el de la ciudad al lado.
--
-- Aire: solo cuentan las estaciones fijas (las móviles cambian de sitio). Una estación
-- entra en el mes si tiene promedio diario en al menos el 75 % de los días transcurridos.
-- La localidad es el promedio de sus estaciones; la ciudad, el de todas. Las localidades
-- sin estación no tienen fila: el sitio las muestra como "sin medición" (SPEC §9).
with dia as (
    select d.estacion_id, e.localidad_id, d.fecha, d.promedio
    from {{ ref('fct_aire_estacion_dia') }} d
    join {{ ref('dim_estacion') }} e using (estacion_id)
    where d.contaminante = 'pm25' and not e.es_movil
),

corte as (
    select date_trunc('month', fecha) as mes, max(fecha) filter (where promedio is not null) as fecha_corte
    from dia
    group by 1
),

estacion_mes as (
    select
        d.estacion_id,
        d.localidad_id,
        date_trunc('month', d.fecha) as mes,
        count(d.promedio) as dias_validos,
        avg(d.promedio) as pm25_promedio,
        100.0 * count(*) filter (where d.promedio > 15) / nullif(count(d.promedio), 0) as pct_dias_sobre_oms
    from dia d
    group by all
),

estacion_valida as (
    select m.*, c.fecha_corte
    from estacion_mes m
    join corte c using (mes)
    where m.dias_validos >= 0.75 * (date_diff('day', m.mes, c.fecha_corte) + 1)
),

largo as (
    select estacion_id, localidad_id, mes, fecha_corte, 'aire_pm25_promedio' as indicador_id, pm25_promedio as valor
    from estacion_valida
    union all
    select estacion_id, localidad_id, mes, fecha_corte, 'aire_pm25_dias_sobre_guia_oms', pct_dias_sobre_oms
    from estacion_valida
),

ciudad as (
    select mes, indicador_id, avg(valor) as valor_ciudad
    from largo
    group by all
)

select
    l.localidad_id,
    cast(l.mes as date) as mes,
    l.indicador_id,
    round(avg(l.valor), 2) as valor,
    round(any_value(c.valor_ciudad), 2) as valor_ciudad,
    count(*) as n_observaciones,
    max(l.fecha_corte) as fecha_corte_fuente
from largo l
join ciudad c using (mes, indicador_id)
group by all
