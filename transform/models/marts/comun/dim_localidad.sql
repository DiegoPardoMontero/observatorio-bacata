-- Las 20 localidades con su nombre canónico y las estaciones fijas de la RMCAB que tienen.
select
    l.localidad_id,
    l.nombre,
    l.slug,
    l.es_rural,
    count(e.estacion_id) as n_estaciones_aire,
    coalesce(list(e.nombre order by e.nombre) filter (e.estacion_id is not null), []) as estaciones_aire
from {{ ref('localidad') }} l
left join {{ ref('estacion') }} e
    on e.localidad_id = l.localidad_id and not e.es_movil
group by all
order by l.localidad_id
