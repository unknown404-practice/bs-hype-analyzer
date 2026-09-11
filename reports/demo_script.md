# 🎬 BS & Hype Analyzer — Competition Demo Video Script

**Target Duration**: 3 minutes 30 seconds  
**Format**: Loom / YouTube screen recording with picture-in-picture presenter camera  
**Target Audience**: Data science judges, quantitative portfolio managers, financial compliance officers, intelligence analysts  
**Key Value Proposition**: 100% local multi-modal NLP, graph echo-chamber detection, interactive Jupyter dashboard, zero cloud API dependencies  

---

## ⏱️ Scene-by-Scene Storyboard & Script

### Act 1: The Problem — Information Pollution & Financial FOMO (0:00 - 0:35)
- **Visual**: Split screen showing extreme headlines: *"CRASH OR RALLY? Wall Street Strategists Issue Urgent Warning!"* and YouTube thumbnails with glowing red arrows and *"100x GUARANTEED"*.
- **Presenter (Voiceover)**:
  > *"Every single trading day, investors and consumers are bombarded with sensational financial media and influencer hyperbole. Headline algorithms optimize for rage and FOMO rather than truth. Retail traders get liquidated chasing 100x moonshots, while institutional desks waste hours sifting through manufactured hype. We built the AI-Powered BS & Hype Analyzer to turn the tables on information pollution—running 100% locally on your machine with zero cloud leaks."*

---

### Act 2: Multi-Modal Ingestion & Local Architecture (0:35 - 1:10)
- **Visual**: Show `assets/architecture.png` diagram on screen, then transition into `notebooks/01_ingest_rss_and_youtube.ipynb`.
- **On-Screen Action**: Run cell ingesting both RSS articles across 10 major outlets (Bloomberg, Reuters, CNBC, CoinDesk) and local Whisper transcription of a YouTube finance influencer.
- **Presenter (Voiceover)**:
  > *"Sensationalism doesn't stay confined to print. Our engine is natively multi-modal. In Notebook 01, we ingest feeds across 10 diverse media categories, while our audio ingestion module extracts audio tracks via `yt-dlp` and transcribes spoken speech using OpenAI Whisper running entirely on local CPU/GPU hardware. No data ever leaves your computer, making it enterprise-ready for proprietary trading desks."*

---

### Act 3: The 5-Factor Linguistic Hype Decomposition (1:10 - 1:50)
- **Visual**: Switch to `notebooks/02_feature_engineering_and_hype_scores.ipynb`. Display the distribution histogram and the 5-Factor Radar Chart.
- **On-Screen Action**: Highlight the comparison between an objective Reuters wire story (Score: 0.08) and a sensational broadcast article (Score: 0.88).
- **Presenter (Voiceover)**:
  > *"Rather than relying on black-box sentiment, we deconstructed hype into a mathematical 5-factor model: superlative buzzword density, sentiment subjectivity, clickbait syntax, vague anonymous citations like 'experts warn', and an empirical grounding penalty that flags qualitative assertions devoid of numeric data. Look at this diagnostic radar: the sensational claim saturates all 5 dimensions, while the objective wire release stays grounded at zero."*

---

### Act 4: The Narrative Echo-Chamber Graph (1:50 - 2:30)
- **Visual**: Switch to `notebooks/03_echo_chamber_graph.ipynb`. Show the interactive Plotly network graph and PyVis force-directed physics graph.
- **On-Screen Action**: Hover over nodes, rotate the graph, highlight the high-hype cluster connecting CNBC, MarketWatch, and YouTube influencers.
- **Presenter (Voiceover)**:
  > *"Here is our winning edge: the Echo-Chamber Graph. Sensational stories spread like contagion. By calculating hybrid Jaccard entity overlap and lexical alignment between articles, we map how narratives propagate. Notice the community clusters: the high-hype cluster in red forms a self-reinforcing echo loop, while wire services cluster separately. Using PageRank centrality, we can programmatically pinpoint the exact media outlets acting as echo epicenters."*

---

### Act 5: Executive Dashboard & Live Interactive Triage (2:30 - 3:10)
- **Visual**: Open `notebooks/04_interactive_dashboard.ipynb`.
- **On-Screen Action**:
  1. Adjust the Hype Threshold slider from 0.50 to 0.70 (watch KPI cards update in real time).
  2. Type `"Bitcoin"` into the search box (charts filter instantly).
  3. Click an article in the drilldown inspector to view the highlighted buzzwords and 5-factor diagnostic radar.
- **Presenter (Voiceover)**:
  > *"In Notebook 04, we bring everything together in an interactive executive dashboard built with Plotly and ipywidgets. Analysts can adjust decision thresholds in real time, filter by sector, search for specific corporate tickers like Nvidia or Bitcoin, and inspect any article's linguistic fingerprint. It's an instant radar shield against market manipulation."*

---

### Act 6: Wrap-Up, Business Impact & Reproduction (3:10 - 3:30)
- **Visual**: Show `README.md`, the clean green test suite passing (`18 passed in 4s`), and the CLI terminal.
- **Presenter (Voiceover)**:
  > *"The BS & Hype Analyzer is 100% reproducible with a single `make all` command, verified by unit tests, and fully documented. By transforming unstructured text and spoken audio into auditable, quantitative intelligence, we help investors see through the noise. Thank you!"*

---

## 📋 Recording Checklist
- [x] Precomputed sample Parquet generated in `data/processed/`
- [x] HTML figures generated in `reports/figures/`
- [x] Pytest suite verified (`18 passed`)
- [x] Notebooks run and cleared/pre-rendered as desired
- [x] Microphones calibrated, screen resolution set to 1080p (1920x1080)
