-- Aviso y no error mientras seguridad no se publique (ver _staging.yml).
{{ config(severity='warn') }}
-- Un conteo de delitos no puede ser negativo (la variación porcentual sí).
select localidad_id, fecha_corte, delito_codigo, anio, valor
from {{ ref('stg_sdscj__delito_alto_impacto') }}
where medida = 'conteo' and valor < 0
