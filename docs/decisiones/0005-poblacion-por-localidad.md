# 0005 — Población por localidad: proyecciones DANE-SDP de agosto de 2025

- **Estado:** aceptada
- **Fecha:** 2026-09-25
- **Requerimientos:** RF-13, RF-12, RNF-06 (habilita las tasas por 100.000 habitantes de la SPEC §9)

## Contexto

La SPEC (§4) marca la población por localidad y año como faltante transversal: sin ella no hay tasas por 100.000 habitantes, y sin tasas no se puede publicar seguridad (§9) ni comparar siniestros viales entre localidades. La §9 deja abierta la pregunta de qué fuente se usa como oficial.

## Qué encontramos

Datos Abiertos Bogotá tiene dos conjuntos con población por localidad de 2005 a 2035, los dos con licencia CC BY 4.0:

| | Planeación (SDP) | Salud (SDS) |
| --- | --- | --- |
| Dataset | [Proyecciones y retroproyecciones de Población (2005 - 2035)](https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035) | [Población en Bogotá D.C. 2005-2035](https://datosabiertos.bogota.gov.co/dataset/piramide-poblacional-bogota-d-c) |
| Versión de las proyecciones | Marzo de 2025 (`202503_localidad_…ods`) | Agosto de 2025: "Contrato Interadministrativo 500 de 2025 - DANE, SDP y Región Metropolitana Bogotá Cundinamarca" (según su archivo de metadatos) |
| Formato | ODS ancho: una columna por sexo y edad (0 a 100 y más), filas por localidad, año y área (cabecera o rural) | CSV largo, separado por `;`, UTF-8 con BOM: `ANO;CODIGO_LOCALIDAD;NOMBRE_LOCALIDAD;SEXO;EDAD;CURSODEVIDA;GRUPOEDAD;POBLACION` |
| Actualización en el portal | 14 may 2025 | 2 may 2026 |
| Total de Bogotá | No viene aparte | Viene como localidad `0` |

- En el CSV de Salud, la suma de las 20 localidades es exactamente el total de Bogotá en los 31 años. Bogotá tiene 7.945.996 habitantes en 2026.
- De 2005 a 2017 las dos versiones son idénticas. Desde 2018 se separan: de 2018 a 2026, 18 localidades difieren menos de 4 %, Los Mártires hasta 11 % menos en la versión de agosto (75.373 frente a 83.567 en 2026) y Sumapaz hasta 9 % menos (3.385 frente a 3.698). Hacia 2035 las diferencias crecen hasta 8 % en otras localidades.
- Leer el ODS exige una dependencia más (`odfpy`); el CSV se lee con la biblioteca estándar.

## Decisión

La población oficial del Observatorio son las proyecciones DANE-SDP-RMBC de agosto de 2025, tomadas del CSV de la Secretaría de Salud.

- `scripts/semilla_poblacion.py` descarga el CSV (busca el recurso por nombre en `package_show`), suma sexos y edades y escribe `transform/seeds/poblacion_localidad.csv`: `localidad_id`, `anio`, `poblacion`, 20 localidades × 31 años.
- Es una semilla y no un extractor del pipeline porque la fuente cambia muy pocas veces: se vuelve a correr a mano si el DANE publica una revisión.
- **Validaciones del script:** se detiene si cambian las columnas, si falta una localidad o el total de Bogotá en algún año de 2005 a 2035, si aparece un código extra, si un nombre no coincide con la semilla de localidades (sin distinguir tildes) o si las localidades no suman el total de la ciudad. Hay pruebas sin conexión en `tests/test_semilla_poblacion.py`.
- **Gold:** `dim_localidad_anio` (`localidad_id`, `anio`, `poblacion`, `poblacion_ciudad`). La población no va en `dim_localidad` porque cambia cada año y esa tabla tiene una fila por localidad. dbt prueba la unicidad de localidad y año, la relación con `dim_localidad`, los rangos y que cada año tenga las 20 localidades.

## Por qué la de agosto y no la de Planeación

- Es la más reciente y la hicieron el DANE y la SDP juntos, así que reemplaza a la de marzo.
- El CSV largo se valida mejor: trae el total de la ciudad para comprobar la suma.
- La publica otra entidad (Salud), pero la fuente que cita es la misma SDP con el DANE. Si Planeación publica la versión de agosto, se cambia la URL del script y nada más.

## Consecuencias

- Las tasas por 100.000 habitantes quedan listas para seguridad (RF-13) y siniestros viales (RF-12). La tasa de un año usa la población de ese año.
- Las fichas de localidad muestran la población estimada del año en curso, con su fuente.
- Todos los años son estimaciones, también los anteriores al censo de 2018. Si hay una revisión, las tasas de años pasados cambian; la metodología lo advierte.
- Sumapaz tiene unos 3.400 habitantes: una tasa por 100.000 con tan pocos habitantes salta mucho con un solo caso. Cuando se publiquen tasas, Sumapaz va aparte (SPEC §9).

## Pendiente

- Preguntar a la SDP si publicará la versión de agosto de 2025 en su propio dataset.
- Si una fase necesita población por edad (por ejemplo, tasas de siniestros de menores), el CSV la trae: bastaría no sumar las edades.
