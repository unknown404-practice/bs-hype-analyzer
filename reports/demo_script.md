# 🎙️ Rehearsed 2–3 Minute Hackathon Demo Script
**Project**: AI-Powered BS & Hype Analyzer  
**Duration**: 2 minutes 45 seconds  
**Format**: Screen share with presenter voiceover (or live stage presentation)  
**Pre-requisite**: Run `make all` before the demo so all sample features and graphs are ready.  

---

### Part 1: The Real-World Problem (0:00 – 0:30)
- **Visual**: Show the project title and [Figure 1 (Hype Spectrum)](../reports/figures/hype_histogram.png).
- **Voiceover**:
  - *"Every day, financial media and social influencers blast retail investors with hyperbolic headlines—screaming '100x moonshots' or warning of an 'overnight bloodbath'."*
  - *"These algorithms optimize for rage and clicks, not accuracy, leading to capital misallocation and painful liquidations."*
  - *"We built the **BS & Hype Analyzer** to solve this: an open-source, 100% local multi-modal pipeline that quantifies sensationalism, maps echo-chambers, and gives investors an objective radar shield."*

---

### Part 2: The Live Interactive Dashboard (0:30 – 1:30)
- **Visual**: Open [`notebooks/04_interactive_dashboard.ipynb`](../notebooks/04_interactive_dashboard.ipynb) in JupyterLab Desktop.
- **Action**:
  - Point to the top KPI cards: 151 media items analyzed, contrasting outlets pre-selected.
  - Show the **Min Hype Slider** (currently set at **0.25**, the 70th percentile).
  - Drag the slider up to **0.50**: watch the flagged count filter down to the most extreme sensational articles.
  - Toggle the outlet dropdown from *Contrasting Trio* to *CNBC Markets*, then to *Reuters Business*.
  - Point out the **Linguistic Radar Chart**:
    - *"Notice how CNBC spikes on superlative density, clickbait syntax, and anonymous 'experts say' citations."*
    - *"In contrast, Reuters stays grounded at zero subjectivity with dense quantitative statistics."*
  - Type `"Bitcoin"` or `"Nvidia"` into the search box to show instant zero-latency filtering.

---

### Part 3: The Echo-Chamber Graph & Narrative Contagion (1:30 – 2:20)
- **Visual**: Switch to browser with [`reports/figures/echo_chamber_graph.html`](../reports/figures/echo_chamber_graph.html) (or [Figure 3](../reports/figures/echo_chamber_labeled.png)).
- **Action**:
  - Drag the graph nodes around to show the ForceAtlas2 physics simulation.
  - Point out the three modularity communities:
    - *"In red, we have the High-Hype Speculation Cluster—connecting CNBC, MarketWatch, CoinDesk, and YouTube financial influencers."*
    - *"In green, the Institutional Wire Cluster—Reuters, WSJ, and Financial Times."*
  - Highlight the PageRank epicenters:
    - *"Network centrality reveals that CNBC and WSJ act as the primary narrative bridges transmitting niche crypto and stock hype into the mainstream."*

---

### Part 4: Closing & 100% Local Reproducibility (2:20 – 2:45)
- **Visual**: Return to [`README.md`](../README.md) showing the green badges and `make all` command.
- **Voiceover**:
  - *"What gives our tool its winning edge is that it is 100% local: no data leaks to third-party APIs, making it compliant for institutional trading desks."*
  - *"Anyone can clone the repo and reproduce our entire pipeline in under 5 minutes with `make all`."*
  - *"Thank you—let's bring transparency back to financial information."*

---

### ⏱️ Rehearsal Time Allocation
| Section | Goal | Target Time |
| :--- | :--- | :---: |
| **1. Problem & Impact** | Set the stakes (FOMO, liquidations, information pollution) | 0:30 |
| **2. Live Dashboard** | Sliders, KPI tiles, contrast CNBC vs Reuters, radar chart | 1:00 |
| **3. Echo-Chamber Graph** | Communities, narrative links, PageRank epicenters | 0:50 |
| **4. Wrap-Up** | 100% local, zero cloud leaks, 5-minute `make all` | 0:25 |
| **Total** | | **2:45** |
