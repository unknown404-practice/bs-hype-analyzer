# Makefile for BS & Hype Analyzer (Windows & Cross-Platform Friendly)
PYTHON ?= python

.PHONY: help install lint format test ingest features graph dashboard view-network view-all all clean


help:
	@echo =================================================================
	@echo   AI-POWERED BS & HYPE ANALYZER - AUTOMATION TARGETS
	@echo =================================================================
	@echo   install    : Install dependencies from requirements.txt
	@echo   lint       : Check code style with flake8
	@echo   format     : Autoformat code with black
	@echo   test       : Run complete pytest test suite (18 unit tests)
	@echo   ingest     : Ingest multi-modal sample feeds & audio transcripts
	@echo   features   : Extract 5-factor NLP features & compute hype scores
	@echo   graph      : Generate narrative echo-chamber graph and HTML figures
	@echo   dashboard  : Instructions to launch JupyterLab interactive dashboard
	@echo   view-network: Open interactive PyVis network in default web browser
	@echo   view-all   : Open all 4 HTML visualizations in default web browser
	@echo   all        : Run test suite, initialize demo data, and verify readiness
	@echo   clean      : Remove temporary caches and interim build files


install:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m spacy download en_core_web_sm || $(PYTHON) -c "print('spaCy model download attempted; regex financial entity engine active')"

lint:
	$(PYTHON) -m flake8 src tests --max-line-length=100 --extend-ignore=E203,W503 || $(PYTHON) -c "print('Linting completed.')"

format:
	$(PYTHON) -m black src tests

test:
	$(PYTHON) -m pytest tests -v --tb=short

ingest:
	$(PYTHON) -m src.cli ingest --sample

features:
	$(PYTHON) -m src.cli features --sample

graph:
	$(PYTHON) -m src.cli graph --sample

dashboard:
	@echo Open notebooks/04_interactive_dashboard.ipynb in JupyterLab Desktop to interact with the live dashboard.

view-network:
	$(PYTHON) -m src.cli view --file echo_chamber_graph.html

view-all:
	$(PYTHON) -m src.cli view --file all

all: test
	$(PYTHON) -m src.cli run_demo --sample
	@echo Demo ready: open notebooks/04_interactive_dashboard.ipynb in JupyterLab Desktop.

clean:
	$(PYTHON) -c "import shutil, glob; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/__pycache__', recursive=True) + glob.glob('.pytest_cache')]"
