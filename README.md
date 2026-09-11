# BS & Hype Analyzer

AI-powered analyzer that quantifies media hype and maps narrative echo chambers — 100% local, privacy-preserving, reproducible in 5 minutes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 22/22 Passing](https://img.shields.io/badge/tests-22%2F22%20passing-brightgreen.svg)](tests/)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Local: 100% Offline](https://img.shields.io/badge/privacy-100%25%20local-success.svg)](#)

---

## 🎯 What is this?

Modern financial and technology news cycles are saturated with hyperbolic rhetoric, fear-mongering headlines, and circular citations. Retail investors, researchers, and consumers make high-stakes decisions based on media that often prioritizes sensationalism over verifiable facts. This information pollution distorts price discovery, amplifies market panics, and erodes public trust.

The **BS & Hype Analyzer** provides an objective, automated antidote. Ingesting multi-modal streams — from wire RSS feeds to financial YouTube broadcasts — it transcribes speech locally with OpenAI Whisper, extracts linguistic signals with spaCy, and calculates a rigorous **5-Factor Hype Score**. It then applies graph theory (NetworkX, PageRank, Greedy Modularity) to map cross-outlet co-amplification and expose circular echo chambers.

With this tool, you can instantly see which outlets produce the most sensationalized coverage, trace how speculative narratives propagate across the media landscape, and filter out high-hype noise.

- **100% local execution (no external APIs, no data leaks).**
- **Designed for investors, educators, and anyone who wants clearer signal in noisy media.**

---

## 🚀 Quickstart (5 minutes)

Follow these steps to run the complete pipeline with pre-cached benchmark data on Windows, macOS, or Linux:

### 1. Clone the repository
```bash
git clone https://github.com/unknown404-practice/bs-hype-analyzer.git
cd bs-hype-analyzer
```

### 2. Create and activate a virtual environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install dependencies and NLP model
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Run the automated pipeline
```bash
make all
```
*(On Windows systems without `make`, run: `python -m src.cli run-demo`)*

### 5. Launch the interactive dashboard
Open **`notebooks/04_interactive_dashboard.ipynb`** in **JupyterLab Desktop** and run all cells.

> [!NOTE]
> All sample datasets are pre-cached in `data/raw/`. The entire demo executes 100% offline with zero external API calls or network access required.

---

## 📊 What you’ll see

- **Interactive Executive Dashboard**: Dynamic control panel in `04_interactive_dashboard.ipynb` featuring real-time KPI metrics, interactive threshold sliders, outlet filters, and a **5-Factor Radar Diagnostic Chart** showing the linguistic fingerprint of any article.
- **Hype Score Distribution & Outlet Comparisons**: High-contrast Plotly dark-theme histograms and comparative bar charts contrasting institutional wire baselines (Reuters, WSJ) against sensationalist outlets.
- **Echo-Chamber Network Graph**: A structural network visualization exposing narrative subcultures — from the *Speculative Frenzy Cluster* (CNBC, MarketWatch, YouTube Crypto) to the *Institutional Wire Baseline* — with PageRank highlighting narrative transmission bridges.
- **Native JupyterLab Desktop HTML Viewer**: Open **`notebooks/view_html_reports.ipynb`** to inspect all interactive HTML reports (`echo_chamber_graph.html`, `network_plotly.html`, etc.) in a unified 4-tab interface directly inside JupyterLab Desktop without needing an external browser.

---

## 🧠 How it works (at a glance)

- **5-Factor Hype Score**: Combines superlative density, sentiment subjectivity, clickbait syntax, vague authority shielding, and quantitative grounding disparity into a calibrated $0.0 \text{ to } 1.0$ score.
- **Echo-Chamber Graph**: Media outlets are linked by named entity Jaccard overlap and shared content n-grams; modularity clustering reveals narrative subcultures, while PageRank pinpoints central media epicenters.
- **Multi-Modal Ingestion**: Financial RSS feeds and YouTube influencer audio tracks are ingested and transcribed locally with Whisper STT on CPU/GPU.

For full architectural and mathematical details, see **[docs/architecture.md](docs/architecture.md)** and **[docs/metrics.md](docs/metrics.md)**.

---

## 📁 Repository structure

```text
├── config/              # YAML & JSON configuration for feeds and hype hyperparameters
├── data/                # 3-tier data lifecycle: raw, interim, and processed (sample data included)
├── docs/                # Detailed documentation (architecture, metrics, structure)
├── notebooks/           # End-to-end JupyterLab workflow (00–04 + view_html_reports.ipynb)
├── reports/figures/     # Interactive HTML simulations, Plotly figures, and PNG charts
├── src/                 # Core production modules (config, ingest, features, graph, viz, cli)
└── tests/               # Pytest suite with 22 unit tests (100% passing)
```

For a complete folder and file breakdown, see **[docs/structure.md](docs/structure.md)**.

---

## 🛠 Tech stack

- **Core & NLP**: Python 3.12, spaCy (`en_core_web_sm`), TextBlob, Transformers (PyTorch).
- **Speech & Audio**: OpenAI Whisper / faster-whisper, yt-dlp.
- **Network Science & Math**: NetworkX, NumPy, Pandas, Scipy.
- **Visualization**: PyVis (ForceAtlas2 physics), Plotly, ipywidgets.
- **Environment & Automation**: JupyterLab Desktop, pytest, Makefile, Click CLI.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Creator & Contact

- **Creator**: **Ranadeep Saha**
- **Email**: [ranadeep2021saha@gmail.com](mailto:ranadeep2021saha@gmail.com)
- **GitHub**: [https://github.com/unknown404-practice](https://github.com/unknown404-practice)
- **LinkedIn**: [https://www.linkedin.com/in/ranadeep-saha-a03296404/](https://www.linkedin.com/in/ranadeep-saha-a03296404/)
- Member of **Google Developer Group**

---

## 🏆 Why this project stands out

- **Real-World Impact**: Directly addresses information pollution and sensationalism in financial media, helping users distinguish factual wire reporting from viral speculation.
- **Technical Depth**: Integrates local speech-to-text, NLP feature engineering, graph-theoretic community detection, and physics-based network simulation in a cohesive pipeline.
- **Reproducibility**: 5-minute setup with cached benchmark data, deterministic seeds, cross-platform Makefile automation, and a 22/22 passing test suite.
- **Portfolio-Ready Engineering**: Modular clean architecture, typed dataclasses, complete documentation hub, and native JupyterLab Desktop interactive reporting.
