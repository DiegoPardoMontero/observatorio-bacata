-- Víctimas de siniestros viales desde 2021, una fila por víctima (ADR 0006).
--
-- Bronze tiene un archivo por año de ocurrencia. Si la SDM corrige la fecha de una víctima
-- y la pasa a un año que no se volvió a bajar, quedaría en dos archivos: vale la
-- extracción más reciente.
with ultima_carga as (
    select *
    from {{ source('bronze', 'sdm__victima') }}
    qualify row_number() over (partition by codigo_accidentado order by fecha_extraccion desc) = 1
)

select
    codigo_accidentado as victima_id,
    formulario,
    localidad_codigo as localidad_id,
    fecha_ocurrencia as fecha,
    cast(date_trunc('month', fecha_ocurrencia) as date) as mes,
    try_cast(hora_ocurrencia as time) as hora,
    case capa when 'MUERTO' then 'muerto' when 'LESIONADO' then 'herido' end as estado,
    -- peaton, ciclista, motociclista, conductor o pasajero
    lower(condicion) as actor,
    -- En qué iba el pasajero (motociclista, pasajero de bus…)
    case when condicion = 'PASAJERO' then lower(condicion_a) end as modo_pasajero,
    lower(clase_acc) as clase,
    muerte_posterior = 'S' as muerte_posterior,
    fecha_extraccion
from ultima_carga
