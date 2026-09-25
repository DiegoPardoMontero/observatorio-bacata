-- Mediciones horarias de la RMCAB, limpias y tipadas (reglas de la ADR 0001).
with ultima_carga as (
    -- El mismo día se descarga varias veces: vale la extracción más reciente
    select *
    from {{ source('bronze', 'rmcab__horario') }}
    qualify row_number() over (
        partition by estacion_codigo, parametro, fecha_hora_fuente
        order by fecha_extraccion desc
    ) = 1
),

tipada as (
    select
        estacion_codigo as estacion_id,
        parametro,
        unidad,
        -- La fuente marca cada hora por su final (01:00 es de 00:00 a 01:00).
        -- Aquí cada hora se identifica por su inicio, en hora de Bogotá.
        cast(fecha_hora_fuente as timestamp) - interval 1 hour as fecha_hora,
        estado_valido_portal and valor <> -9999 as es_valida,
        valor,
        estado,
        fecha_extraccion
    from ultima_carga
)

select
    estacion_id,
    parametro,
    unidad,
    fecha_hora,
    cast(fecha_hora as date) as fecha,
    case when es_valida then valor end as valor,
    es_valida,
    estado,
    fecha_extraccion
from tipada
