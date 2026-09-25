# 0001 — Extraer la RMCAB desde el reporte horario del portal

- **Estado:** aceptada (prueba de la Fase 0)
- **Fecha:** 2026-09-25
- **Requerimientos:** RF-08, RF-09

## Contexto

La RMCAB no tiene API ni exportación documentada (SPEC §4), y depender de su portal es el riesgo técnico más alto del proyecto (SPEC §9). La Fase 0 pide demostrar la extracción con un mes de PM2.5 de 3 estaciones en Parquet.

## Qué encontramos

**Fuente:** `GET http://rmcab.ambientebogota.gov.co/Report/HourlyReports?id=1&UserDateString=AAAA-MM-DD`

- Responde sin login ni cookies. Cada día pesa unos 8 MB de HTML y tarda unos 2 s.
- Trae las 19 estaciones del portal (la SPEC habla de 20), dos de ellas móviles (Móvil 7ma y Móvil Fontibón), con todos sus monitores: 27 parámetros en agosto de 2026 entre contaminantes, meteorología y carbono negro.
- La tabla visible no sirve: redondea los valores y no trae el estado del dato. Los datos completos están en el `onclick` de cada casilla del gráfico: `graph('<estación>', …, '<datos JSON>', <catálogo JSON>, '<canal>', '<unidad>', …)`. Cada registro es `{"DATE_TIME": …, "<PARÁMETRO>": valor, "STATUS<canal>": código}`, y el catálogo trae el nombre de la estación, la unidad y la regla de completitud (`PctValid: 75`).
- **El canal no identifica el parámetro.** El canal 18 es PM2.5 en Centro de Alto Rendimiento y ozono en Guaymaral. El parámetro sale de la llave del valor.
- **Cada hora se marca por su final:** `01:00` es el promedio de 00:00 a 01:00, y la hora 24 aparece como `00:00` del día siguiente. Todo va en hora de Bogotá (UTC−5, sin horario de verano).
- **Los faltantes vienen de tres formas:** la fila no existe (en Jazmín, el 15 de agosto no hay filas de 14:00 a 18:00), el valor es `-9999`, o el código de estado no es válido.
- **Estados:** la página incluye `StatusDic`, que dice qué códigos muestra el portal (`true`) y cuáles oculta. Los códigos `true` son 1, 14, 29–34, 77–83, 85, 86, 89 y 93–95. En agosto de 2026 aparecieron: 1 (171.436 filas), 0 (13.325), 4 (3.467), 18 (906), 9 (751), 109 (610), 3 (469) y 8 (4). De esos, solo el 1 es válido. Todos los `-9999` tienen un estado no válido (casi siempre 0; en 11 casos, 4 u 8). No sabemos qué significa cada código.
- `robots.txt` no existe (404).
- El portal falla a ratos: durante la carga de agosto respondió 500 a cualquier fecha por unos minutos y después se recuperó solo.

## Alternativas descartadas

- **`HourlyReportsInAdvance`** (rango de fechas): devuelve un PDF y tardó 36 s para 3 días. Con `DisplayFor=HTML` devuelve una página sin datos.
- **`ExportAllHourlyReportsToExcel`**: el sitio verifica la sesión (`/home/getsession`) antes de exportar. No lo exploramos más porque el JSON embebido ya trae todo, incluido el estado.
- **Leer la tabla visible:** los valores vienen redondeados y sin estado.

## Decisión

Se extrae un día por petición desde `HourlyReports`, se lee el JSON embebido y se guarda en Bronze sin limpiar nada.

- Código en `extract/rmcab.py`. Un día: `make extract-rmcab FECHA=AAAA-MM-DD`. Históricos: `python -m extract.rmcab --desde … --hasta …`.
- Bronze va en `data/bronze/rmcab__horario/fecha_carga=AAAA-MM-DD/<fecha_reporte>.parquet`, en formato largo: `estacion_codigo`, `estacion_nombre`, `canal`, `parametro`, `unidad`, `fecha_hora_fuente`, `valor`, `estado`, `estado_valido_portal`, `fecha_reporte`, `fecha_extraccion` y `hash_pagina`. Se guardan todas las estaciones y parámetros, porque la página viene completa de todas formas.
- **Prueba de contrato:** la extracción se detiene si falta `StatusDic`, si no hay series, si un registro trae otras llaves o si las horas no corresponden a la fecha pedida. Esto último protege contra un portal que ignore la fecha y devuelva otro día. Hay pruebas sin conexión, con un recorte real de la página en `tests/fixtures/rmcab/`, y una contra el portal real (`pytest -m red`).
- **Trato con el portal:** hasta 5 intentos con esperas de 10 a 80 s, pausa de 3 s entre días y un `User-Agent` que identifica al proyecto.

## Resultado de la prueba

Agosto de 2026 completo: 31 días, 190.968 filas, 19 estaciones y 27 parámetros, en 1,5 MB de Parquet y unos 2 minutos de descarga.

| Estación | Horas con PM2.5 válido (de 744) | Promedio del mes (µg/m³) | Máximo horario (µg/m³) |
| --- | --- | --- | --- |
| Kennedy | 741 (99,6 %) | 9,9 | 42,8 |
| Tunal | 739 (99,3 %) | 6,3 | 27,0 |
| Usaquén | 739 (99,3 %) | 3,1 | 16,5 |

Casi todas las estaciones superan el 96 % de horas válidas de PM2.5. Las excepciones son Ciudad Bolívar (17,6 %), Colina (86,3 %) y Las Ferias (92,1 %).

## Consecuencias

- Aire es viable como primer tema: con una petición por hora del día en curso se puede cumplir la frescura de RNF-02, aunque falta medir con cuánto retraso aparece la hora más reciente.
- La extracción es frágil: depende de detalles del HTML (el `onclick`, la función `graph`, `StatusDic`). Si el proveedor cambia la página, la prueba de contrato falla en vez de guardar datos malos.
- Para Silver quedan estas reglas: válido = `estado_valido_portal`; `-9999` pasa a nulo; `fecha_hora_fuente` se convierte a inicio de hora en hora de Bogotá; se deduplica entre cargas (el mismo día se recarga varias veces); y los promedios diarios usan la regla de completitud del 75 % (`PctValid`).
- Cada petición baja unos 8 MB, así que una por hora suma unos 190 MB al día. Es aceptable en GitHub Actions.

## Pendiente

- Pedir a la Secretaría de Ambiente acceso formal o un volcado, que sigue como decisión abierta en la SPEC: la extracción funciona, pero es frágil.
- Confirmar la licencia de los datos.
- Averiguar qué significa cada código de estado (0, 3, 4, 8, 9, 18 y 109).
- Aclarar por qué el portal muestra 19 estaciones y la SPEC dice 20.
- Medir con qué retraso publica el portal la hora más reciente.
