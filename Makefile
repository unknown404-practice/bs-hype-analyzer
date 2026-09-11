# Makefile for BS & Hype Analyzer
PYTHON ?= python

.PHONY: help install lint format test ingest features graph dashboard all clean

help:
	@echo "Available targets:"
	@echo "  install    : Install python dependencies"
	@echo "  lint       : Check code style with flake8"
	@echo "  format     : Autoformat code with black"
	@echo "  test       : Run pytest test suite"
	@echo "  ingest     : Run multi-modal ingestion (RSS & YouTube)"
	@echo "  features   : Extract NLP metrics & compute hype scores"
	@echo "  graph      : Generate echo-chamber citation/co-occurrence graph"
	@echo "  dashboard  : Launch interactive Jupyter dashboard"
	@echo "  all        : Run full pipeline (ingest -> features -> graph -> test)"
	@echo "  clean      : Remove temporary caches and interim build files"

install:
	$(PYTHON) -m pip install -r requirements.txt

lint:
	$(PYTHON) -m flake8 src tests --max-line-length=100 --extend-ignore=E203,W503 || echo "Linting completed with notices."

format:
	$(PYTHON) -m black src tests

test:
	$(PYTHON) -m pytest tests -v --tb=short

ingest:
	$(PYTHON) -m src.cli ingest --use-sample

features:
	$(PYTHON) -m src.cli features

graph:
	$(PYTHON) -m src.cli graph

dashboard:
	jupyter lab notebooks/04_interactive_dashboard.ipynb

all: ingest features graph test

clean:
	$(PYTHON) -c "import shutil, pathlib, glob; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/__pycache__', recursive=True) + glob.glob('.pytest_cache')]"
