# System Architecture Overview

The **BS & Hype Analyzer** is engineered as a decoupled, 4-tier pipeline designed for 100% local, privacy-preserving execution. It ingests multi-modal media data, calculates linguistic sensationalism scores, maps cross-outlet narrative echo chambers, and presents decision-ready diagnostics in interactive interfaces.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      4-TIER SYSTEM PIPELINE ARCHITECTURE                │
├─────────────────────────────────────────────────────────────────────────┤
│ Tier 1: Multi-Modal Ingestion (RSS Text Feeds + Local Whisper Audio STT) │
│                                   │                                     │
│                                   ▼                                     │
│ Tier 2: NLP Feature Engineering & 5-Factor Hype Scoring Engine          │
│                                   │                                     │
│                                   ▼                                     │
│ Tier 3: Graph Echo-Chamber & Narrative Alignment Engine (NetworkX)      │
│                                   │                                     │
│                                   ▼                                     │
│ Tier 4: Presentation & Decision Interfaces (JupyterLab Desktop + CLI)   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Tier 1: Multi-Modal Ingestion Layer

The ingestion subsystem (`src/ingest.py`) unifies disparate media channels into a standardized schema (`data/interim/ingested_articles.csv`):
- **RSS Text Feeds**: Polls financial and tech wire feeds (e.g., Reuters, Bloomberg, WSJ, CNBC, CoinDesk) via `feedparser`. HTML content is sanitized and stripped of styling, scripts, and ads using `BeautifulSoup4`.
- **YouTube Audio Tracks**: Extracts audio streams from video feeds via `yt-dlp` and transcribes spoken audio locally using OpenAI's `whisper` (or `faster-whisper`) on CPU/CUDA with zero remote API transmission.
- **Offline Fallbacks**: Automatically falls back to deterministic, pre-ingested benchmark datasets (`data/raw/`) when network access is unavailable, guaranteeing 100% offline reproducibility.

---

## Tier 2: NLP Feature Engineering & Scoring Engine

The linguistic processing engine (`src/features.py`) extracts quantitative features from raw text:
- **Tokenization & Entity Extraction**: Leverages `spaCy` (`en_core_web_sm`) to tag parts-of-speech, named entities (tickers, organizations, persons), and syntactical constructs.
- **5 Orthogonal Linguistic Dimensions**:
  1. *Superlative & Buzzword Density* ($S_{sup}$)
  2. *Sentiment Subjectivity* ($S_{subj}$) via `TextBlob`
  3. *Clickbait Typographic & Syntactic Signals* ($S_{click}$)
  4. *Vague & Anonymous Authority Shielding* ($S_{vague}$)
  5. *Quantitative Grounding Disparity* ($S_{unsub}$)
- **Composite Score Engine**: Calculates the calibrated hype score $H \in [0, 1]$ scaled by empirical outlet priors, persisted into high-performance columnar formats (`data/processed/sample_features.parquet`).

---

## Tier 3: Graph Echo-Chamber & Narrative Alignment Engine

The network analytics subsystem (`src/graph.py`) models media cross-citation and narrative synchronization:
- **Entity & Lexical Overlap**: Evaluates inter-outlet narrative alignment via Jaccard entity overlap and top-$k$ content n-gram similarity.
- **Network Construction**: Builds an attributed undirected graph (`NetworkX`) where nodes represent media outlets and edge weights reflect narrative co-amplification above threshold $\tau_{\text{edge}} = 0.15$.
- **Graph Algorithms**:
  - *Greedy Modularity Community Detection*: Partitions the media landscape into distinct narrative subcultures (Speculative Frenzy, Institutional Baseline, Tech Commentary).
  - *PageRank & Centrality*: Quantifies structural influence to identify key narrative amplifiers transmitting sensationalism into mainstream coverage.

---

## Tier 4: Presentation & Decision Interfaces

The final tier (`src/viz.py`, `src/cli.py`) translates analytical data into actionable visual formats:
- **Native JupyterLab Desktop Viewer**: A tabbed `ipywidgets` interface (`notebooks/view_html_reports.ipynb`) embedding interactive PyVis physics simulations and Plotly dark charts using local `srcdoc` iframes without external browser dependencies.
- **Interactive Control Dashboard**: Notebook `04_interactive_dashboard.ipynb` enables dynamic filtering by outlet, threshold tuning, and single-article 5-factor radar diagnostics.
- **Sub-Second Terminal CLI**: Immediate text triage via `python -m src.cli analyze "headline"`.
