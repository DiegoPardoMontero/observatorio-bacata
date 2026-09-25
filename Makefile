PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
FECHA ?= $(shell TZ=America/Bogota date +%F)

.PHONY: all extract transform site extract-rmcab extract-sdscj

all: extract transform site

extract: extract-rmcab extract-sdscj

extract-rmcab:
	$(PYTHON) -m extract.rmcab --fecha $(FECHA)

extract-sdscj:
	$(PYTHON) -m extract.sdscj

transform:
	@echo "transform: pendiente (dbt build)"

site:
	@echo "site: pendiente (build del sitio)"
