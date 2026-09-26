-- Víctimas de siniestros viales por localidad, mes, estado y tipo de actor (RF-12, ADR 0006).
--
-- Son conteos. Cómo comparar localidades (conteo, tasa por residentes o las dos) está por
-- decidir: la localidad es donde ocurrió el siniestro, no donde vive la víctima (ADR 0006).
-- Los dos meses más recientes se siguen digitando y van marcados como provisionales.
with victima as (
    select * from {{ ref('stg_sdm__victima') }}
),

corte as (
    select max(fecha) as fecha_corte from victima
)

select
    v.localidad_id,
    v.mes,
    v.estado,
    v.actor,
    count(*) as victimas,
    v.mes >= cast(date_trunc('month', c.fecha_corte) - interval 1 month as date) as es_provisional,
    c.fecha_corte as fecha_corte_fuente
from victima v
cross join corte c
group by all
order by v.localidad_id, v.mes, v.estado, v.actor
