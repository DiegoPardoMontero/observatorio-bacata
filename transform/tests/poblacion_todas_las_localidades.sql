-- Cada año tiene las 20 localidades: si falta una, sus tasas saldrían sin denominador
-- y el total de la ciudad quedaría corto (ADR 0005).
select anio, count(*) as localidades
from {{ ref('dim_localidad_anio') }}
group by anio
having count(*) <> (select count(*) from {{ ref('localidad') }})
