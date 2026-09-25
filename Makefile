PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
DBT ?= $(if $(wildcard .venv/bin/dbt),.venv/bin/dbt,dbt)
FECHA ?= $(shell TZ=America/Bogota date +%F)

.PHONY: all extract transform site extract-rmcab extract-sdscj

all: extract transform site

extract: extract-rmcab extract-sdscj

extract-rmcab:
	$(PYTHON) -m extract.rmcab --fecha $(FECHA)

extract-sdscj:
	$(PYTHON) -m extract.sdscj

# dbt corre desde la raíz: las rutas de DuckDB, Bronze y Gold son relativas a ella
transform:
	$(DBT) build --project-dir transform --profiles-dir transform

# Se borra la caché de los data loaders: Framework solo los vuelve a correr si
# cambia el código del loader, no si cambian los datos de Bronze.
site:
	rm -rf site/src/.observablehq/cache/data
	cd site && ([ -d node_modules ] || npm ci) && npm run build
