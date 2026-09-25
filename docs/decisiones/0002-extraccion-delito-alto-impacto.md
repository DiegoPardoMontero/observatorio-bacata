# 0002 — Extraer Delito de Alto Impacto desde los GeoJSON de Datos Abiertos Bogotá

- **Estado:** aceptada (prueba de la Fase 0)
- **Fecha:** 2026-09-25
- **Requerimientos:** RF-13, RF-14

## Contexto

La SPEC (§4) describe esta fuente como "mensual, ene. 2018 – ago. 2026, por localidad" y como la más limpia de las cuatro. La Fase 0 pide probar su extracción antes de construir sobre ella.

## Qué encontramos

**Fuente:** el dataset [Delito de Alto Impacto. Bogotá D.C.](https://datosabiertos.bogota.gov.co/dataset/delito-de-alto-impacto-bogota-d-c), que se consulta con `package_show` en la API CKAN del portal. Tiene 10 descargas (SHP, KMZ, DXF, GPKG y GeoJSON, cada una en dos versiones) y un servicio REST de ArcGIS (`oaiee.scj.gov.co/agc/rest/services/Tematicos_Pub/CifrasSCJ/MapServer/0`).

- **No es una serie mensual.** Cada archivo es un acumulado del año a la fecha por localidad. El campo `CMMES` dice qué periodo trae: `Ene-Ago (2025vs2026)` significa que cada columna suma los delitos de enero a agosto de su año, desde 2018 hasta 2026. Hay dos versiones: el acumulado del año en curso (`Ene-Ago`, actualizado el 21 sep 2026) y el año anterior completo (`Ene-Dic (2024vs2025)`, del 29 ene 2026).
- **Cada mes se reemplaza el archivo.** El recurso conserva su identificador desde 2022 y el contenido se sobrescribe, así que el acumulado de julio ya no existe. Internet Archive solo tiene una copia de cada archivo, de agosto de 2022.
- **Formato ancho:** 21 filas (las 20 localidades y `99 Sin Localización`) y una columna por delito y año (`CMH26CONT` = homicidios de 2026). Además, por delito, trae la variación porcentual frente al año anterior (`CMHVAR`) y el total de la ciudad (`CMHTOTAL`). Son 11 delitos: homicidios, lesiones personales, hurto a personas, a residencias, de automotores, de bicicletas, a comercio, de celulares y de motocicletas, delitos sexuales y violencia intrafamiliar.
- **Los nombres de campo están cortados a 10 caracteres** porque el GeoJSON sale de un shapefile: `CMHCE18CON` en el GeoJSON es `CMHCE18CONT` en el servicio REST.
- **La fecha de corte no viene como dato.** Sale del periodo (`Ene-Ago` de 2026 → 31 ago 2026), y la descripción de la capa REST la confirma ("Fecha de corte 31 agosto 2026").
- **Licencia:** CC BY-SA 4.0. Los derechos son de la Secretaría Distrital de Seguridad, Convivencia y Justicia (SDSCJ).
- **El servicio REST y el GeoJSON coinciden** en 2.520 de 2.541 valores. Las 21 diferencias son lesiones personales de 2026: el REST las trae nulas y el GeoJSON las trae en 0, en todas las localidades. Es decir, en el GeoJSON un 0 puede ser un dato faltante.

### Los dos archivos no cuadran entre sí

Si los datos fueran consistentes, el acumulado de enero a agosto de un año dividido por el año completo daría cerca de 0,67 (8 de 12 meses). Estos son los cocientes para toda la ciudad:

| Delito | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| H | 0,64 | 0,62 | 0,63 | 0,67 | 0,65 | 0,66 | 0,62 | 0,68 |
| LP | 0,70 | 0,69 | 0,57 | 0,65 | 0,71 | 0,62 | 0,64 | 0,61 |
| HP | 1,61 | 1,64 | 1,54 | 1,46 | 1,30 | 0,67 | 0,66 | 0,71 |
| HR | 1,94 | 1,88 | 1,85 | 1,94 | 1,35 | 0,67 | 0,69 | 0,69 |
| HA | 1,32 | 1,34 | 1,18 | 1,21 | 1,25 | 0,66 | 0,71 | 0,67 |
| HB | 0,68 | 0,64 | 0,66 | 0,70 | 0,64 | 0,74 | 0,74 | 0,82 |
| HC | 2,42 | 2,13 | 2,56 | 3,29 | 3,28 | 3,17 | 2,47 | 3,03 |
| HCE | 0,08 | 0,09 | 0,09 | 0,11 | 0,10 | 0,07 | — | 0,10 |
| HM | 6,91 | 6,59 | 4,93 | 3,65 | 3,06 | 1,62 | 1,41 | 1,37 |
| DS | 0,68 | 0,66 | 0,63 | 0,64 | 0,69 | 0,58 | 0,68 | 0,73 |
| VI | 0,71 | 0,64 | 0,66 | 0,64 | 0,68 | 0,56 | 0,62 | 0,64 |

- Homicidios, lesiones personales, hurto de bicicletas, delitos sexuales y violencia intrafamiliar cuadran en todos los años.
- **Hurto a comercio, de celulares y de motocicletas no cuadran en ningún año**, y el patrón se parece a una rotación de columnas. Si el comercio del acumulado se compara con los celulares del año completo, el cociente da entre 0,60 y 0,76 en todos los años. Desde 2023, celulares contra motos y motos contra comercio también dan entre 0,65 y 0,84. Todavía no sabemos cuál de los dos archivos tiene las columnas bien.
- **Hurto a personas, a residencias y de automotores no cuadran de 2018 a 2022** (cocientes de 1,2 a 1,9) y sí desde 2023. Puede ser un cambio de metodología que solo se aplicó a uno de los archivos, pero no está documentado.
- En el año completo, hurto de celulares de 2024 es 0 en todas las localidades.

El problema está en la fuente, no en la descarga: el servicio REST en vivo trae los mismos valores que el GeoJSON.

## Alternativas descartadas

- **Servicio REST** (`MapServer/0/query`): trae los nombres de campo completos y distingue nulo de 0, pero solo publica el acumulado del año en curso. No trae el año anterior completo. Queda como referencia para confirmar valores.
- **SHP, GPKG, KMZ y DXF:** son el mismo contenido en otros formatos. El GeoJSON se lee sin dependencias adicionales.
- **WFS:** misma capa que el REST.

## Decisión

Se descargan todos los recursos GeoJSON del dataset y se guardan en Bronze sin corregir nada.

- Código en `extract/sdscj.py`. Se corre con `make extract-sdscj`, y `make extract` lo incluye.
- Los recursos se encuentran por formato en `package_show`, sin fijar sus identificadores. Así, si el portal cambia un recurso, la extracción lo sigue encontrando.
- Bronze va en `data/bronze/sdscj__delito_alto_impacto/fecha_carga=AAAA-MM-DD/<fecha_corte>.parquet`, en formato largo, con una fila por localidad y campo: `localidad_codigo`, `localidad_nombre`, `periodo_fuente`, `fecha_corte`, `campo` (el nombre original), `medida` (`conteo`, `variacion_pct` o `total_ciudad`), `delito_codigo`, `anio`, `valor`, `recurso_id`, `recurso_nombre`, `recurso_modificado` (el `last_modified` de CKAN), `fecha_extraccion` y `hash_archivo`.
- Se descarta la geometría, porque los polígonos oficiales vienen del dataset de localidades de Planeación. También se descartan `SHAPE_AREA` y `SHAPE_LEN`.
- **Prueba de contrato:** la extracción se detiene si el zip no trae exactamente un `.geojson`, si no están las 21 localidades, si el archivo mezcla periodos o el periodo no se puede leer, si aparece un campo o un delito desconocido, si a una localidad le falta un año entre 2018 y el año del corte, si un conteo está repetido (por ejemplo, si llegan el nombre cortado y el completo) o si un valor no es numérico. Hay pruebas sin conexión con el GeoJSON real sin geometría (`tests/fixtures/sdscj/`) y una contra la fuente real (`pytest -m red`).

## Resultado de la prueba

Dos recursos en 9 s: `Ene-Ago (2025vs2026)` con 2.541 filas y `Ene-Dic (2024vs2025)` con 2.310. El total de la ciudad (`CMHTOTAL`) coincide con la suma de las localidades: 740 homicidios de enero a agosto de 2026.

## Consecuencias

- **RF-13 ("por localidad y mes") no sale directo de esta fuente.** Para tener meses hay que guardar cada acumulado mensual y restar el anterior: agosto = (enero a agosto) − (enero a julio). Por eso Bronze conserva cada carga en su propia partición. La historia mensual anterior a la primera carga no se puede reconstruir desde aquí.
- Lo que sí se puede mostrar sin inventar nada es el acumulado del año a la fecha, comparado con el mismo periodo de años anteriores. Eso cumple RF-14 (cada localidad frente a sí misma) con frecuencia anual.
- Silver no puede usar hurto a comercio, de celulares ni de motocicletas, ni los hurtos de 2018 a 2022, hasta que la SDSCJ aclare las diferencias. Los ceros del GeoJSON se tienen que comparar con el REST antes de tratarlos como dato.
- La frecuencia diaria que propone la SPEC §7 sirve: basta detectar un cambio en `recurso_modificado` o en `hash_archivo`.
- La SPEC §4 se corrige para describir la fuente como es.

## Pendiente

- Preguntar a la SDSCJ (Oficina de Análisis de la Información y Estudios Estratégicos) cuál de los dos archivos es el correcto para hurto a comercio, de celulares y de motocicletas, y por qué cambian los hurtos de 2018 a 2022.
- Buscar una serie mensual por localidad: los boletines mensuales de la SDSCJ o una petición directa. Hay que resolverlo antes de la Fase 3.
- Sigue faltando la población por localidad y año para calcular tasas (SPEC §4, faltante transversal).
