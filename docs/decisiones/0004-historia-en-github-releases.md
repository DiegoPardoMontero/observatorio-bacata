# 0004 — La historia de Bronze vive en GitHub Releases

- **Estado:** aceptada
- **Fecha:** 2026-09-25
- **Requerimientos:** RNF-01, RNF-02, RNF-07, RNF-08

## Contexto

Cada corrida de GitHub Actions empieza sin archivos, pero el sitio necesita la historia: meses de datos de aire y cada corte mensual de seguridad. La SPEC (§7 y §9) dejó abierta la elección entre Cloudflare R2, GitHub Releases y una rama `data`. La decisión se vuelve urgente con el cron horario: sin historia no hay "estado actual" ni series.

## Decisión

Bronze completo se guarda como un solo archivo, `bronze.tar`, en una release del repositorio llamada `bronze` y marcada como prerelease para que no aparezca como versión del sitio.

- `python -m extract.historia bajar` lo descarga y lo desempaca en `data/bronze/` al empezar cada corrida.
- `python -m extract.historia subir` lo empaca y lo sube después de extraer.
- La subida no reemplaza el archivo de una vez. Primero sube `bronze-nuevo.tar`, después renombra el vigente a `bronze-anterior.tar` y por último renombra el nuevo a `bronze.tar`. Si la subida se corta a medias, `bajar` usa el más reciente que exista, y siempre queda una copia de la corrida anterior.
- El pipeline (`.github/workflows/pipeline.yml`) corre cada hora al minuto 23 y hace, en orden: bajar historia, extraer, subir historia, `dbt build`, construir el sitio y publicarlo. Si falla una prueba de dbt, no se publica y queda la versión anterior (RNF-07). Si falla una fuente, se publica igual con lo que hay, y el sitio avisa del retraso.

## Por qué

- **No necesita cuentas ni secretos.** El token de Actions (`contents: write`) basta, y `gh` viene instalado en los runners. R2 exige una cuenta de Cloudflare y llaves guardadas como secretos.
- **Es pequeño.** De enero a septiembre de 2026, la RMCAB pesa unos 7 MB en Parquet. Una corrida baja y sube el archivo completo en segundos. Un asset puede pesar hasta 2 GB.
- **Todo queda en el mismo repositorio**, como pide RNF-01.

## Alternativas descartadas

- **Cloudflare R2:** mejor si los datos crecen mucho, por ejemplo con las validaciones de TransMilenio en la Fase 2. Queda como plan B.
- **Rama `data` en el repositorio:** cada corrida horaria sería un commit con binarios, y el repositorio crecería sin límite.
- **Caché de Actions:** se borra tras 7 días sin uso y no está pensada para guardar datos.

## Consecuencias

- La RMCAB se baja cada hora: el día en curso y, antes de las 4 a. m., también el anterior, porque la hora de 23:00 a 24:00 se publica como 00:00 del día siguiente (`--recientes`). Delito de Alto Impacto se revisa una vez al día, a las 6 a. m., y solo se guarda si el archivo cambió.
- Solo hay dos versiones de la historia, la vigente y la anterior. Si un error pasara las pruebas de contrato y dañara Bronze durante dos corridas seguidas, habría que reconstruirlo desde las fuentes. En el caso de la RMCAB se puede; con Delito de Alto Impacto se perderían los cortes mensuales pasados.
- **Barreras contra la pérdida de historia** (agregadas el 25 sep 2026). Con solo dos versiones, una sola bajada fallida bastaba para perderla: si `gh release view` fallaba por la red, `bajar` lo tomaba como "no hay historia", la corrida subía un Bronze con solo el día actual y la corrida siguiente borraba la última copia completa. Ahora solo "release not found" cuenta como historia vacía y cualquier otro error detiene el pipeline; además, `subir` se niega a reemplazar `bronze.tar` por un archivo de menos del 90 % de su tamaño, porque la historia solo crece (`--forzar` para una reducción intencional). Las pruebas están en `tests/test_historia.py`, con un `gh` falso.
- GitHub desactiva los cron de los repositorios públicos tras 60 días sin actividad (SPEC §9). Todavía no hay nada que lo evite. El 25 de septiembre de 2026 se revisó la salida más usada, la acción `gautamkrishnar/keepalive-workflow` (llama a la API que habilita el workflow o hace un commit vacío): su repositorio aparece "deshabilitado por el personal de GitHub por una violación de los términos de servicio". No se sabe si la causa es el método, pero es señal suficiente para no copiarlo sin revisar los términos. Mientras se decide, la mitigación es manual: la página de estado avisa si el sitio lleva más de 3 horas sin construirse, y basta un commit cualquiera en menos de 60 días para mantener vivo el cron.
- Si la historia pasa de unos cientos de MB, conviene partirla por fuente y mes, o migrar a R2.
