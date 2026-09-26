# Observatorio Bacatá

Los datos abiertos de Bogotá, claros y por localidad: calidad del aire, movilidad, seguridad y costo de vida.

Proyecto cívico, gratuito y de código abierto. Cada cifra del sitio dice de dónde viene y hasta qué fecha llega.

- **Sitio:** https://diegopardomontero.github.io/observatorio-bacata/ (se actualiza cada hora)
- **Especificación:** [docs/SPEC.md](docs/SPEC.md)
- **Decisiones técnicas:** [docs/decisiones/](docs/decisiones/)
- **Sistema de diseño:** [docs/diseno/](docs/diseno/)
- Código bajo MIT · datos derivados bajo CC BY-SA 4.0

## Qué hay publicado

| Tema | Estado | Qué muestra |
| --- | --- | --- |
| Aire | Publicado (Fase 1) | IBOCA por estación cada hora, series horaria y diaria de PM2.5 con la norma y la guía de la OMS, patrón por hora y día, PM2.5 mensual por localidad en el mapa y en las fichas |
| Población | Lista (base común) | Habitantes por localidad y año de 2005 a 2035, para calcular tasas por 100.000 habitantes |
| Movilidad | Extracción lista, sin publicar (Fase 2) | Víctimas de siniestros viales por localidad y tipo de actor desde 2021, en el dataset descargable. Falta decidir cómo comparar localidades ([ADR 0006](docs/decisiones/0006-fuentes-de-movilidad.md)) |
| Seguridad | Extracción lista, sin publicar (Fase 3) | Faltan una serie mensual y que la Secretaría aclare tres hurtos ([ADR 0002](docs/decisiones/0002-extraccion-delito-alto-impacto.md)) |
| Costo de vida | Pendiente (Fase 4) | — |

Además: buscador de localidad, mapa de las 20 localidades, una ficha por localidad, descargas en CSV y Parquet, metodología y una página de estado de las fuentes.

## Cómo funciona

```
Fuentes ──extract/──▶ Bronze (Parquet crudo) ──dbt + DuckDB──▶ Silver ──▶ Gold (Parquet) ──▶ site/ (Observable Framework) ──▶ GitHub Pages
```

Todo corre en GitHub Actions cada hora ([pipeline.yml](.github/workflows/pipeline.yml)), sin servidores ni servicios de pago. La historia de Bronze se guarda entre corridas en la release `bronze` del repositorio ([ADR 0004](docs/decisiones/0004-historia-en-github-releases.md)). Si una prueba de dbt falla, no se publica y queda la versión anterior.

| Carpeta | Qué tiene |
| --- | --- |
| `extract/` | Un extractor por fuente, con pruebas de contrato: se detiene antes que guardar datos malos |
| `transform/` | Proyecto dbt: staging (`stg_`), dimensiones (`dim_`) y hechos (`fct_`), con sus pruebas |
| `site/` | Sitio estático: páginas en Markdown, data loaders en Python que leen Gold, componentes en `site/src/components/` |
| `scripts/` | Generadores de semillas y geometrías que se corren a mano (estaciones, polígonos, población) |
| `tests/` | Pruebas de los extractores y scripts, sin conexión (`pytest -m red` consulta las fuentes reales) |

## Correrlo en local

Necesitas Python 3.12 y Node 20 o más reciente.

```sh
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
make all                      # extrae hoy, transforma y construye el sitio en site/dist
cd site && npm run dev        # vista previa con recarga
```

Otros comandos:

```sh
make extract-rmcab FECHA=2026-09-01                             # un día de la RMCAB
.venv/bin/python -m extract.rmcab --desde 2026-01-01 --hasta 2026-01-31   # un rango
.venv/bin/python -m extract.historia bajar                       # la historia de producción (necesita gh)
dbt build --project-dir transform --profiles-dir transform       # modelos y pruebas, desde la raíz
.venv/bin/python -m pytest tests/                                # pruebas de Python
```

## Fuentes

| Fuente | Entidad | Licencia |
| --- | --- | --- |
| [RMCAB, reporte horario](http://rmcab.ambientebogota.gov.co/Report/HourlyReports) | Secretaría Distrital de Ambiente | Por confirmar |
| [Delito de Alto Impacto](https://datosabiertos.bogota.gov.co/dataset/delito-de-alto-impacto-bogota-d-c) | Secretaría Distrital de Seguridad, Convivencia y Justicia | CC BY-SA 4.0 |
| [Población por localidad 2005-2035](https://datosabiertos.bogota.gov.co/dataset/piramide-poblacional-bogota-d-c) | DANE y Secretaría Distrital de Planeación (publica la Secretaría de Salud) | CC BY 4.0 |
| [Siniestralidad (SIGAT)](https://datos.movilidadbogota.gov.co/search?tags=siniestralidad) | Secretaría Distrital de Movilidad | Por confirmar |
| [Localidad. Bogotá D.C.](https://datosabiertos.bogota.gov.co/dataset/localidad-bogota-d-c) | Catastro Distrital (IDECA) | CC BY 4.0 |

## Reglas que no se negocian

- La unidad es la localidad. En seguridad, nunca barrio ni punto.
- Seguridad siempre en tasas por 100.000 habitantes y nunca en rankings ([SPEC §9](docs/SPEC.md)).
- Una localidad sin estación de aire dice "sin medición": no se interpola.
- Todo en español, en lenguaje claro.
