.PHONY: setup install test clean visualize run-all

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

install:
	$(PIP) install -e ".[dev]"

test:
	$(VENV)/bin/pytest --tb=short -v

clean:
	rm -rf $(VENV) dist build *.egg-info .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Genera el mapa y el perfil de elevación a partir de un CSV existente.
# Uso: make visualize CSV=mi_ruta_data.csv
visualize:
	$(PYTHON) dibujar_ruta.py $(CSV)

# Extrae los datos de un GPX y genera inmediatamente el mapa y el perfil.
# Uso: make run-all GPX=actividad.gpx
run-all:
	$(VENV)/bin/read-gpx $(GPX)
