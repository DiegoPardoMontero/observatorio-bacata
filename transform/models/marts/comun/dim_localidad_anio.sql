-- Población de cada localidad por año, el denominador de las tasas por 100.000 habitantes
-- (SPEC §9). Proyecciones y retroproyecciones DANE-SDP de agosto de 2025 (ADR 0005); todos
-- los años son estimaciones, también los anteriores al censo de 2018.
-- La población va aparte de dim_localidad porque cambia cada año.
select
    p.localidad_id,
    p.anio,
    p.poblacion,
    sum(p.poblacion) over (partition by p.anio) as poblacion_ciudad
from {{ ref('poblacion_localidad') }} p
join {{ ref('localidad') }} l using (localidad_id)
order by p.localidad_id, p.anio
