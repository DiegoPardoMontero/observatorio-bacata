# 0003 — Prueba del sitio con Observable Framework

- **Estado:** propuesta (prueba de la Fase 0; falta decidir si se prueba Astro)
- **Fecha:** 2026-09-25
- **Requerimientos:** RF-09, RF-17, RF-19, RNF-03, RNF-04, RNF-05, RNF-06

## Contexto

La SPEC deja abierta la elección entre Observable Framework y Astro (§9) y pide una prueba de un día con Framework en la Fase 0 (§10): una página con un gráfico publicada en GitHub Pages. El sistema de diseño llegó el mismo día (`docs/diseno/`), así que la prueba también sirve para ver si Framework se deja vestir con él. El paquete de diseño sugiere Astro o Next.js, pero no por nada específico de Framework: pide un sitio estático con poco JavaScript.

## Qué se construyó

- `site/`: proyecto de Framework 1.13.4 con una sola página, `src/index.md`: "¿Cómo estuvo el aire en agosto?". Muestra el PM2.5 diario de agosto de 2026 en Kennedy, Tunal y Usaquén, con el límite diario de la Resolución 2254 de 2017 (37 µg/m³) y la guía de la OMS (15 µg/m³) como referencia.
- El data loader `src/data/pm25_diario.csv.py` lee Bronze con DuckDB y aplica las reglas de la ADR 0001: horas válidas, deduplicación entre cargas, hora marcada por su final y mínimo de 18 horas válidas por día.
- La página trae un resumen en texto que se calcula con los datos, una tabla con todas las cifras, la descarga del CSV, la fuente y la fecha de corte, y una sección "Cómo se calculó".
- `make site` construye el sitio. `.github/workflows/sitio.yml` lo publica en GitHub Pages en cada push a master.

## Qué encontramos

**Funcionó sin pelear**

- **Data loaders en Python.** Framework corre `python3` por defecto. Con la opción `interpreters`, la configuración usa `.venv/bin/python` si existe. Los loaders corren con el directorio de trabajo en `site/`, así que las rutas se arman desde `__file__`.
- **El sistema de diseño entra casi tal cual.** Con `style`, la hoja propia reemplaza el tema. Se importa la base de Framework (`observablehq:default.css` y `theme-air`) y encima los tokens y componentes directamente desde `docs/diseno/design/`. El bundler resuelve rutas fuera de `src/`, así que el sistema de diseño tiene una sola fuente de verdad y no hay copias.
- **Observable Plot** alcanza para este tipo de gráfico: small multiples por estación, líneas de referencia, etiquetas selectivas, tooltip y ancho adaptable con `resize`. Acepta variables CSS como colores, así que las marcas usan los tokens de datos.
- **Peso:** 216 KB comprimidos con gzip en la carga inicial (625 KB sin comprimir), más las fuentes de Google. Está por debajo del 1 MB de RNF-03. El LCP no se midió.
- **Móvil:** a 360 px no hay scroll horizontal y el gráfico se ajusta al ancho (RNF-04).

**Hubo que rodearlo**

- **No hay opción para el idioma del documento:** el HTML sale con `<html>` sin `lang`, lo que incumple WCAG 3.1.1. `site/scripts/idioma.js` agrega `lang="es"` después de cada build.
- **La caché de los loaders no ve los datos:** Framework vuelve a correr un loader solo si cambia su código, no si cambia Bronze. `make site` borra `src/.observablehq/cache/data` antes de construir. En CI no importa, porque cada corrida empieza sin caché.
- **El layout trae opiniones:** cabecera fija, barra lateral, índice y paginador. Se apagaron las tres últimas (`sidebar`, `toc`, `pager`) y se sobrescribió el CSS de la cabecera para que quede como en el diseño.
- **Un `href="${…}"` en HTML rompe el build**, porque Framework lo toma como la ruta de un archivo estático. Los enlaces a archivos van con la ruta literal (`data/pm25_diario.csv`), y así Framework además copia el archivo al sitio.
- **`base` solo afecta la página 404.** Todas las demás rutas son relativas, así que el mismo build sirve en local y en GitHub Pages.
- **Tema oscuro:** Framework lo activa solo con `prefers-color-scheme`, pero el sistema de diseño no define uno. Se fijó el tema claro.

**No se probó**

- Páginas con parámetros, como `/localidad/{slug}` para las 20 fichas (RF-06). Framework las soporta con `[slug].md` y `dynamicPaths`.
- El mapa en SVG (RF-03) y el buscador (RF-02).

## Bronze en CI

`data/` no está en git, así que en GitHub Actions no hay Bronze. El workflow descarga agosto de 2026 del portal de la RMCAB (31 peticiones) y lo guarda en la caché de Actions con una llave fija. Si la caché expira tras 7 días sin uso, se vuelve a descargar. Así se prueba además lo que más importa para el cron horario de la SPEC: si GitHub Actions puede llegar al portal. Esto no reemplaza la decisión abierta entre R2 y Releases para guardar la historia entre corridas (SPEC §9).

## Decisión

Framework sirve para el Observatorio: se construyó la página completa con el sistema de diseño en un día, y los problemas encontrados tienen salida. La recomendación es seguir con Framework y no gastar otro día en Astro, salvo que las fichas por localidad o el mapa muestren un problema en la Fase 1.

## Consecuencias

- El sitio vive en `site/` y se construye con `make site`, o con `make all` después de extraer.
- Los tokens del sitio son los de `docs/diseno/design/tokens/`. Si cambia el diseño, se cambia allí.
- Las fuentes vienen de Google Fonts, como dice el sistema de diseño. No dejan cookies, pero Google ve la IP de cada visita. Si se quiere cumplir RNF-09 con más rigor, hay que servirlas desde el propio sitio.
