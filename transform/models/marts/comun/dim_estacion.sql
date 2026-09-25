-- Estaciones de la RMCAB con su localidad (semilla generada por scripts/semilla_estaciones.py).
select
    e.estacion_id,
    e.sigla_sda,
    e.nombre,
    e.localidad_id,
    l.nombre as localidad,
    e.latitud,
    e.longitud,
    e.es_movil,
    e.mide_pm25,
    e.mide_pm10,
    e.direccion
from {{ ref('estacion') }} e
join {{ ref('localidad') }} l using (localidad_id)
