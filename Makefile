PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
FECHA ?= $(shell TZ=America/Bogota date +%F)

.PHONY: all extract transform site extract-rmcab

all: extract transform site

extract: extract-rmcab

extract-rmcab:
	$(PYTHON) -m extract.rmcab --fecha $(FECHA)

transform:
	@echo "transform: pendiente (dbt build)"

site:
	@echo "site: pendiente (build del sitio)"
