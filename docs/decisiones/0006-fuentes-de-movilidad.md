# 0006 — Fuentes de movilidad: siniestros del SIGAT y validaciones de TransMilenio

- **Estado:** aceptada para siniestros (extracción y modelo de datos); la presentación en el sitio queda abierta
- **Fecha:** 2026-09-26
- **Requerimientos:** RF-11, RF-12, RNF-02, RNF-10

## Contexto

La SPEC (§4 y §9) describe las fuentes de movilidad como desactualizadas: el histórico de siniestros llega hasta octubre de 2021 y las validaciones mensuales hasta diciembre de 2024. Pide explorar el portal de la Secretaría de Movilidad (SDM) y el de TransMilenio antes de la Fase 2. Esta ADR recoge esa exploración (25 y 26 sep 2026).

## Qué encontramos

### Siniestros: `Siniestralidad_BD` de la SDM (base SIGAT)

**Fuente:** `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer`, ítem de ArcGIS Online `ea243e7de8e846c8bd27e47c08771d66` de la cuenta `SecretariaMovilidad`, enlazado desde [datos.movilidadbogota.gov.co](https://datos.movilidadbogota.gov.co/search?tags=siniestralidad).

- **Está al día.** El 26 sep 2026 el siniestro más reciente era del 22 sep 2026. El ítem dice que se actualiza "todos los días con respecto a lo que el grupo de digitadoras haya registrado en SIGAT". Solo se observó una vez, así que la frecuencia real falta confirmarla.
- **Capas:** 0 `MUERTO` (una fila por víctima fallecida), 1 `LESIONADO` (una por víctima herida), 2 `ACCIDENTE` (una por siniestro) y tablas de actores, causas, vehículos y vías. Todas se unen por `FORMULARIO`, el número del informe policial (IPAT). ArcGIS Server 11.3, `maxRecordCount` 2.000, solo `f=json`. Filtrar siempre por año: las consultas agrupadas sobre toda la capa responden 500.
- **Localidad:** campo `LOCALIDAD`, en mayúsculas y sin tildes, con Ñ (`ANTONIO NARIÑO`, `CIUDAD BOLIVAR`) y con `CANDELARIA` sin el artículo. Desde 2021 no tiene nulos. Cruzado con los polígonos de Catastro, coincide en el 99,3 % de los siniestros de 2024; las diferencias están en los bordes.
- **Tipo de actor:** `CONDICION` vale `PEATON`, `CICLISTA`, `MOTOCICLISTA`, `CONDUCTOR` o `PASAJERO`; `CONDICION_A` dice en qué iba el pasajero. Muertos de 2024: 225 peatones, 242 motociclistas, 68 ciclistas, 53 pasajeros y 12 conductores (600).
- **Fechas:** `FECHA_OCURRENCIA_ACC` es la medianoche UTC del día local (13 ene 2026 llega como `1768262400000`, y `DIA_OCURRENCIA_ACC` dice martes). Se lee como fecha en UTC, sin convertir a hora de Bogotá.
- **Retraso de digitación:** los heridos de agosto de 2026 (1.083) están un 25 % por debajo de los meses anteriores, y los de septiembre casi no aparecen. Los muertos se digitan más rápido, pero siguen cambiando: 230 de las 600 víctimas fatales de 2024 murieron después del día del siniestro (`MUERTE_POSTERIOR = 'S'`).
- **Datos personales:** las capas de víctimas traen `GENERO`, `EDAD` y `DIRECCION`, y la de vehículos, la placa.
- **Licencia:** el ítem no declara ninguna. Los demás ítems de datos abiertos de la SDM y el histórico en Datos Abiertos Bogotá son CC BY 4.0.

**De 2007 a 2020 cada siniestro aparece dos veces** (en 2008, hasta tres), con el mismo número de formulario y distinto prefijo (`A000907643` y `AA000907643`). La copia con el prefijo más largo no distingue ciclistas ni motociclistas: los registra como `CONDUCTOR`. Desde 2021 solo hay prefijo `A` y no hay duplicados. Además, desde 2023 casi no se registran los choques con solo daños (41.076 en 2019, 1.115 en 2023), así que el total de siniestros no se puede comparar entre años; las víctimas sí.

| Año | Heridos | Muertos |
| --- | --- | --- |
| 2021 | 18.369 | 470 |
| 2022 | 21.500 | 560 |
| 2023 | 22.971 | 564 |
| 2024 | 22.667 | 600 |
| 2025 | 19.602 | 597 |
| 2026 (al 22 sep) | 11.769 | 471 |

### Validaciones de TransMilenio: el bucket `validaciones_tmsa`

El "documento" del hub de datos de TransMilenio es un bucket público de Google Cloud Storage (`https://storage.googleapis.com/storage/v1/b/validaciones_tmsa/o`), y el recurso de Datos Abiertos Bogotá "por franja horaria" apunta al mismo lugar. **Lo que la SPEC da por desactualizado está al día:** la fecha de diciembre de 2024 es la de los metadatos de CKAN, no la de los archivos.

- **XLSX mensual por estación, acceso e intervalo de 15 minutos** (`ValidacionTroncal/AAAA/MM TM Resumen de Validaciones Troncales … Intervalo 15 Mint.xlsx`): de agosto de 2012 a agosto de 2026, publicado entre 2 y 12 días después de cada mes (el de agosto de 2026, el 9 sep). Unos 14 MB por mes. Suma troncal, dual y cable.
- **Crudos diarios**, una fila por validación: unos 120 MB comprimidos por día solo en troncal, con un seudónimo persistente de cada tarjeta y sus saldos. No sirven para este proyecto: pesan unos 80 GB al año y RF-11 no los necesita.
- **Estaciones:** la capa "Estaciones Troncales" de TransMilenio tiene coordenadas pero no localidad, y unos códigos distintos a los del XLSX (Danubio `9005` y `09005`, Islandia `5009` y `15003`). Cuatro estaciones están en Soacha. La Candelaria y Sumapaz no tienen estaciones troncales.
- **Licencia:** contradictoria. Un recurso de CKAN dice CC BY-SA 4.0 y otro CC BY 4.0, los dos sobre el mismo bucket.

## Alternativas descartadas

- **Histórico de siniestros en Datos Abiertos Bogotá** (`historico-siniestros-bogota-d-c`): un punto por siniestro de 2015 a 2021, sin víctimas ni tipo de actor. Solo sirve para contrastar.
- **Capa `ACCIDENTE` en lugar de las de víctimas:** RF-12 pide víctimas por tipo de actor, y el total de siniestros no es comparable entre años por el corte de 2023 en los choques con solo daños.
- **Agregar en el servidor** (conteos por localidad, actor y mes): es más rápido, pero Bronze dejaría de ser una copia de la fuente y no se podría recalcular nada sin volver a pedirlo.
- **Serie desde 2007:** exige deduplicar formularios con reglas que no están documentadas y deja mal repartidos los tipos de actor en la mitad de los registros. Se deja para después, si hace falta.

## Decisión

**Siniestros (RF-12):** se extraen las víctimas (capas `MUERTO` y `LESIONADO`) desde 2021, una fila por víctima, en `extract/sdm.py`.

- Se piden solo los campos necesarios: `CODIGO_ACCIDENTADO`, `FORMULARIO`, `FECHA_OCURRENCIA_ACC`, `HORA_OCURRENCIA_ACC`, `ANO_OCURRENCIA_ACC`, `CLASE_ACC`, `LOCALIDAD`, `CONDICION`, `CONDICION_A` y, en muertos, `MUERTE_POSTERIOR`. Género, edad y dirección nunca llegan al disco.
- **Bronze no guarda cada carga:** `data/bronze/sdm__victima/anio_ocurrencia=AAAA/victimas.parquet`, un archivo por año que se reemplaza en cada carga, con `fecha_extraccion` adentro. Es distinto de la RMCAB y de la SDSCJ porque la fuente conserva toda su historia (se puede volver a bajar) y los registros se siguen digitando durante semanas: guardar una copia diaria de dos años haría crecer la historia de Bronze en cientos de MB al año, el límite que fija la ADR 0004.
- Cada día se vuelven a bajar el año en curso y el anterior; la primera carga baja desde 2021.
- **Prueba de contrato:** la extracción se detiene si la respuesta trae otros campos, si las filas bajadas no son las que el servidor cuenta para ese año, si aparece una localidad o un tipo de actor desconocido, si una fecha no es del año pedido o si un código de víctima se repite. El nombre de la localidad se convierte a su código (`CANDELARIA` → 17) y Bronze guarda los dos.
- En el pipeline corre una vez al día, como la SDSCJ, y en cada corrida mientras no haya siniestros en Bronze. La corrida diaria también baja cualquier año desde 2021 que falte, así que la primera corrida en CI completa la historia sola (unos 70 s y 1,7 MB).
- **dbt:** `stg_sdm__victima` (una fila por víctima, deduplicada por código con la extracción más reciente) y `fct_movilidad_victima_mes` (conteos por localidad, mes, estado y tipo de actor, con los dos meses más recientes marcados como provisionales). Sus pruebas avisan pero no detienen el pipeline mientras movilidad no se publique, como las de seguridad.

**Validaciones (RF-11):** se construirán después, desde el XLSX mensual de troncal, cruzado por código de estación con una tabla de equivalencias. Una estación es infraestructura, no personas: mostrarla no choca con la regla de no bajar de localidad, que la SPEC (§9, regla 5) fija para seguridad. El aire ya se muestra por estación.

## Decisión abierta: cómo presentar los siniestros por localidad

La SPEC pide comparar localidades con tasas por 100.000 habitantes. Con los siniestros, esa tasa engaña: un siniestro se cuenta en la localidad donde ocurrió, no donde vive la víctima, y las localidades con vías principales, comercio y poca población salen peor. Con los heridos de 2025 (consulta del 26 sep 2026) y la población de 2025 (ADR 0005):

| Localidad | Heridos | Habitantes | Heridos por 100.000 hab. |
| --- | --- | --- | --- |
| Usaquén | 1.045 | 586.286 | 178 |
| Chapinero | 653 | 161.162 | 405 |
| Santa Fe | 695 | 113.315 | 613 |
| San Cristóbal | 850 | 394.686 | 215 |
| Usme | 730 | 399.153 | 183 |
| Tunjuelito | 644 | 175.399 | 367 |
| Bosa | 1.210 | 768.002 | 158 |
| Kennedy | 2.659 | 1.103.801 | 241 |
| Fontibón | 1.311 | 385.455 | 340 |
| Engativá | 1.623 | 831.165 | 195 |
| Suba | 1.899 | 1.251.652 | 152 |
| Barrios Unidos | 680 | 135.332 | 502 |
| Teusaquillo | 852 | 155.083 | 549 |
| Los Mártires | 707 | 75.471 | 937 |
| Antonio Nariño | 478 | 77.392 | 618 |
| Puente Aranda | 1.463 | 249.519 | 586 |
| La Candelaria | 92 | 16.574 | 555 |
| Rafael Uribe Uribe | 857 | 375.043 | 229 |
| Ciudad Bolívar | 1.154 | 685.039 | 168 |
| Sumapaz | 0 | 3.338 | 0 |
| **Bogotá** | 19.602 | 7.942.867 | 247 |

La tabla va en orden de código, no de mayor a menor. Con la tasa por residentes, Los Mártires (937, casi cuatro veces la de Bogotá), Antonio Nariño, Santa Fe, Puente Aranda y La Candelaria quedarían como las "peores", y las localidades residenciales grandes, como Suba y Bosa, como las mejores. Las primeras son céntricas o están cruzadas por grandes vías, con poca población residente y mucho tránsito de gente que vive en otras partes, y el denominador por residentes no mide ese tránsito. Es el tipo de estigma que la SPEC quiere evitar (§1, "Sin estigmas"). Opciones:

1. Conteos absolutos por localidad y tendencia de cada localidad frente a sí misma, sin tasa.
2. Tasa por residentes, con una advertencia visible junto a cada cifra.
3. Las dos, con el conteo como cifra principal.

La recomendación es la 1, con víctimas en los últimos 12 meses (los muertos de un mes en una localidad son muy pocos para compararlos) y sin los dos meses más recientes, que todavía se están digitando. Hasta que se decida, los siniestros no se muestran en las páginas del sitio. Los conteos por localidad, mes y tipo de actor (`fct_movilidad_victima_mes`, sin tasas) sí van en el dataset descargable, porque no ordenan ni califican localidades.

## Consecuencias

- La Fase 2 empieza por siniestros: la fuente está al día, trae localidad y tipo de actor, y la extracción de 2021 en adelante es limpia.
- La SPEC §4 se corrige: las validaciones están al día, y el histórico de siniestros se reemplaza por `Siniestralidad_BD`.
- Los dos meses más recientes de siniestros son provisionales.
- Si la SDM cambia el servicio, la prueba de contrato falla y el sitio conserva la última versión.

## Pendiente

- Confirmar con la Oficina de TIC de la SDM la licencia de `Siniestralidad_BD` y la frecuencia de actualización.
- Confirmar con TransMilenio la licencia del bucket de validaciones.
- Decidir la presentación de los siniestros (arriba).
- Si hace falta la serie desde 2007: entender las familias de prefijos de los formularios y contrastar los muertos deduplicados con la serie oficial.
