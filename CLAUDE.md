# Observatorio Bacatá
Sitio cívico de datos abiertos de Bogotá, por localidad. Especificación: @docs/SPEC.md

# Comandos
- make all: pipeline completo en local (extract, transform, site)
- make extract-<fuente>: corre un extractor (ej. make extract-rmcab FECHA=2026-09-01)
- dbt build --project-dir transform: modelos + tests
- pytest tests/: pruebas de extractores

# Reglas del proyecto
- Todo en español: nombres de modelos, columnas y textos del sitio
- Unidad geográfica base: localidad (dim_localidad). En seguridad, nunca barrio ni punto
- Seguridad: siempre tasas por 100.000 hab., nunca rankings (SPEC sección 9)
- Cada cifra del sitio muestra fuente y fecha de corte
- Sin servidores ni servicios de pago
- Datos crudos y .duckdb fuera de git (ver .gitignore)
- IMPORTANTE: antes de dar algo por terminado, corre dbt build y pytest y muestra la salida

# Flujo
- Una rama por tarea: feat/<RF-xx>-descripcion. PR hacia main, nunca push directo
- Cita el RF de la SPEC en cada commit
- Las decisiones técnicas se registran en docs/decisiones/NNNN-titulo.md
