# Repository Structure & Component Guide

A comprehensive architectural map of the **BS & Hype Analyzer** codebase, outlining directory responsibilities and primary file functions.

---

## Directory Overview

```text
bs-hype-analyzer/
├── assets/                  # Architecture diagrams and visual documentation assets
├── config/                  # Declarative pipeline configurations (feeds & hyperparams)
├── data/                    # 3-tier data lifecycle (raw -> interim -> processed)
│   ├── raw/                 # Seeded benchmark datasets (RSS feeds & YouTube audio transcripts)
│   ├── interim/             # Normalized and sanitized media datasets
│   └── processed/           # Feature-engineered Parquet datasets and graph topology tables
├── docs/                    # Architectural and mathematical documentation hub
│   ├── architecture.md      # 4-tier decoupled pipeline breakdown
│   ├── metrics.md           # Mathematical formulation of hype scores & network graph
│   └── structure.md         # Repository map and file purpose guide (this file)
├── notebooks/               # End-to-end JupyterLab workflow (00–04 + HTML Viewer)
├── reports/                 # Presentation deliverables and visualization exports
│   ├── demo_script.md       # 3.5-minute video presentation storyboard
│   └── figures/             # Standalone interactive HTML reports & publication PNGs
├── scripts/                 # Headless CI automation and smoke test runners
├── src/                     # Core production Python package
└── tests/                   # Pytest test suite (22 unit tests)
```

---

## Core Modules (`src/`)

- **[`src/config.py`](../src/config.py)**: Typed dataclasses (`PipelineConfig`, `HypeWeights`, `FeedConfig`) and loaders that parse `config/hype_config.yaml` and `config/feeds.json` with environment variable overrides.
- **[`src/ingest.py`](../src/ingest.py)**: Multi-modal ingestion engine. Handles RSS parsing via `feedparser`, HTML sanitization via `BeautifulSoup4`, audio stream extraction via `yt-dlp`, and local Whisper speech-to-text.
- **[`src/features.py`](../src/features.py)**: Mathematical NLP pipeline. Performs spaCy entity recognition, TextBlob subjectivity scoring, 5 orthogonal linguistic feature computations, and categorical tier assignments.
- **[`src/graph.py`](../src/graph.py)**: Attributed graph engine. Computes Jaccard entity overlap, constructs NetworkX graphs, prunes noise thresholds, and executes PageRank and greedy modularity community clustering.
- **[`src/viz.py`](../src/viz.py)**: High-aesthetic visualization library. Implements Plotly dark-theme analytics, 100% in-line offline PyVis physics graphs, and native JupyterLab Desktop iframe viewers.
- **[`src/cli.py`](../src/cli.py)**: Production CLI tool supporting batch operations (`ingest`, `features`, `graph`) and instant sub-second text diagnostic triage (`analyze`).

---

## Notebook Workflow (`notebooks/`)

1. **[`00_setup_and_imports.ipynb`](../notebooks/00_setup_and_imports.ipynb)**: Verifies hardware acceleration, installed packages, spaCy model integrity, and directory paths.
2. **[`01_ingest_rss_and_youtube.ipynb`](../notebooks/01_ingest_rss_and_youtube.ipynb)**: Ingests 151 benchmark media items across 10 wire outlets and YouTube audio transcriptions.
3. **[`02_feature_engineering_and_hype_scores.ipynb`](../notebooks/02_feature_engineering_and_hype_scores.ipynb)**: Computes 5 linguistic dimensions and calibrates the composite hype metric.
4. **[`03_echo_chamber_graph.ipynb`](../notebooks/03_echo_chamber_graph.ipynb)**: Builds the media network graph, runs clustering, and generates interactive HTML exports.
5. **[`04_interactive_dashboard.ipynb`](../notebooks/04_interactive_dashboard.ipynb)**: Complete executive dashboard with `ipywidgets` controls, real-time KPI metrics, and radar charts.
6. **[`view_html_reports.ipynb`](../notebooks/view_html_reports.ipynb)**: 4-in-1 tabbed native viewer rendering all interactive HTML reports seamlessly inside JupyterLab Desktop.

---

## Testing & Automation

- **[`tests/`](../tests/)**: Contains 22 comprehensive unit tests spanning features, graph algorithms, ingestion parsers, and offline HTML generation.
- **[`scripts/smoke_test_notebooks.py`](../scripts/smoke_test_notebooks.py)**: Headless test runner executing all notebooks sequentially and confirming zero cell errors.
- **[`Makefile`](../Makefile)**: Cross-platform automation providing single-command targets for setup (`install`), test verification (`test`), pipeline execution (`all`), and dashboard launching (`dashboard`).
