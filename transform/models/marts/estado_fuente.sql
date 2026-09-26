-- Estado de cada fuente para la página de estado del pipeline (RF-20). Las horas son de Bogotá.
-- `limite_retraso_horas`: pasado ese tiempo desde el dato más reciente, el sitio avisa del retraso.
select
    'rmcab' as fuente_id,
    'RMCAB · Secretaría Distrital de Ambiente' as fuente,
    'Calidad del aire por hora' as contenido,
    'Cada hora' as periodicidad,
    3 as limite_retraso_horas, -- RNF-02
    cast(max(fecha_extraccion) at time zone 'America/Bogota' as timestamp) as ultima_extraccion,
    -- Fin de la última hora con dato válido
    max(fecha_hora) filter (where valor is not null) + interval 1 hour as dato_mas_reciente,
    count(*) as registros
from {{ ref('stg_rmcab__medicion') }}

union all

select
    'sdscj',
    'Delito de Alto Impacto · Secretaría de Seguridad',
    'Acumulado del año por localidad',
    'Mensual',
    -- El corte de un mes se publica unos 20 días después; se avisa si pasan 60 días sin corte nuevo
    60 * 24,
    cast(max(fecha_extraccion) at time zone 'America/Bogota' as timestamp),
    cast(max(fecha_corte) as timestamp) + interval 1 day,
    count(*)
from {{ ref('stg_sdscj__delito_alto_impacto') }}

union all

select
    'sdm',
    'Siniestros viales · Secretaría de Movilidad',
    'Víctimas de siniestros por localidad',
    'Diaria',
    -- La SDM publica con unos 3 días de retraso; se avisa si pasa una semana sin datos nuevos
    7 * 24,
    cast(max(fecha_extraccion) at time zone 'America/Bogota' as timestamp),
    cast(max(fecha) as timestamp) + interval 1 day,
    count(*)
from {{ ref('stg_sdm__victima') }}
