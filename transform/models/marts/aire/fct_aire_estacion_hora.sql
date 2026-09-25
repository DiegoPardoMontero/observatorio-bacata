-- Contaminantes por estación y hora (hora de inicio, en hora de Bogotá). Hecho de detalle de aire (SPEC §8).
select
    estacion_id,
    case parametro
        when 'PM2.5' then 'pm25'
        when 'PM10' then 'pm10'
        when 'OZONO' then 'o3'
        when 'NO2' then 'no2'
        when 'SO2' then 'so2'
        when 'CO' then 'co'
    end as contaminante,
    unidad,
    fecha_hora,
    fecha,
    valor,
    es_valida
from {{ ref('stg_rmcab__medicion') }}
where parametro in ('PM2.5', 'PM10', 'OZONO', 'NO2', 'SO2', 'CO')
