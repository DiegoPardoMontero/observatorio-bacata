-- Acumulados del año por localidad y delito (ADR 0002). Todavía no se usa en el sitio,
-- porque la seguridad necesita reglas de presentación y fuentes aclaradas (SPEC §9).
--
-- Bronze guarda cada carga en su partición, y un corte se vuelve a guardar si la SDSCJ
-- cambia el archivo sin cambiar el periodo. Vale la extracción más reciente de cada corte;
-- los cortes distintos (enero-julio, enero-agosto…) se conservan todos.
select
    localidad_codigo as localidad_id,
    fecha_corte,
    periodo_fuente,
    medida,
    delito_codigo,
    anio,
    valor,
    campo,
    recurso_modificado,
    fecha_extraccion,
    hash_archivo
from {{ source('bronze', 'sdscj__delito_alto_impacto') }}
qualify row_number() over (
    partition by localidad_codigo, fecha_corte, medida, delito_codigo, anio
    order by fecha_extraccion desc
) = 1
