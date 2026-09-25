-- Acumulados del año por localidad y delito (ADR 0002). Solo tipado: todavía no se usa en el
-- sitio, porque la seguridad necesita población por localidad para calcular tasas (SPEC §9).
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
