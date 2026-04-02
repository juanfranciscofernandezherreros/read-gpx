.PHONY: setup install test clean

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
