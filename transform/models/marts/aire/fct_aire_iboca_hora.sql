-- IBOCA de PM2.5 por estación y hora, según la Resolución conjunta 2840 de 2023 (RF-08).
--
-- NowCast (art. 5): media ponderada de las últimas 12 horas, incluida la actual.
-- w = Cmin / Cmax de esas horas, con piso de 0,5, y cada hora pesa w^(horas hacia atrás).
-- Las horas sin dato válido se saltan. Se exige dato en al menos 2 de las 3 horas más
-- recientes. La resolución no dice cómo redondear: se trunca a un decimal, como hace la
-- EPA, para que el valor caiga en uno de los intervalos de la Tabla 1.
with pm25 as (
    select estacion_id, fecha_hora, valor
    from {{ ref('stg_rmcab__medicion') }}
    where parametro = 'PM2.5'
),

ventana as (
    select
        h.estacion_id,
        h.fecha_hora,
        date_diff('hour', v.fecha_hora, h.fecha_hora) as horas_atras,
        v.valor
    from pm25 h
    join pm25 v
        on v.estacion_id = h.estacion_id
        and v.fecha_hora between h.fecha_hora - interval 11 hour and h.fecha_hora
        and v.valor is not null
),

factor as (
    select
        estacion_id,
        fecha_hora,
        count(*) filter (where horas_atras <= 2) as validas_ultimas_3,
        case
            when max(valor) <= 0 then 1.0
            else greatest(min(valor) / max(valor), 0.5)
        end as w
    from ventana
    group by estacion_id, fecha_hora
),

nowcast as (
    select
        v.estacion_id,
        v.fecha_hora,
        case
            when f.validas_ultimas_3 >= 2
                then floor(10 * sum(pow(f.w, v.horas_atras) * v.valor) / sum(pow(f.w, v.horas_atras))) / 10
        end as pm25_nowcast
    from ventana v
    join factor f using (estacion_id, fecha_hora)
    group by v.estacion_id, v.fecha_hora, f.validas_ultimas_3
),

-- Concentración para buscar el intervalo: por encima de 500,4 sigue siendo morado (Tabla 1,
-- nota g). Ojo: en DuckDB greatest(NULL, 0) da 0, así que el nulo se trata aparte.
con_intervalo as (
    select
        p.estacion_id,
        p.fecha_hora,
        p.valor as pm25,
        n.pm25_nowcast,
        case when n.pm25_nowcast is not null then least(greatest(n.pm25_nowcast, 0), 500.4) end as c
    from pm25 p
    left join nowcast n using (estacion_id, fecha_hora)
)

select
    x.estacion_id,
    x.fecha_hora,
    cast(x.fecha_hora as date) as fecha,
    x.pm25,
    x.pm25_nowcast,
    -- Índice adimensional (art. 6): interpolación lineal dentro del intervalo
    cast(round((i.i_mayor - i.i_menor) * (x.c - i.c_menor) / (i.c_mayor - i.c_menor) + i.i_menor) as integer) as iboca,
    i.nivel as iboca_nivel,
    i.categoria as iboca_categoria,
    i.color as iboca_color,
    i.color_hex as iboca_color_hex,
    i.nivel_actuacion as iboca_nivel_actuacion
from con_intervalo x
left join {{ ref('iboca_pm25') }} i on x.c between i.c_menor and i.c_mayor
