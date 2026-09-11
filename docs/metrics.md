# Mathematical Metrics & Scoring Formulation

This document details the quantitative methodologies behind the **5-Factor Composite Hype Metric** and the **Echo-Chamber Network Graph** implemented in the BS & Hype Analyzer.

---

## 1. The 5-Factor Composite Hype Metric

The composite hype score ($H \in [0, 1]$) evaluates sensationalism across five orthogonal linguistic dimensions extracted via `src/features.py`:

$$H = \min\left(1.0, \max\left(0.0, \Big(\sum_{i=1}^5 w_i S_i\Big) \cdot \big(0.8 + 0.2 \cdot \Omega_{\text{outlet}}\big)\right)\right)$$

Where the weights $\mathbf{w} = [0.25, 0.25, 0.20, 0.15, 0.15]$ satisfy $\sum w_i = 1.0$, and $\Omega_{\text{outlet}}$ is the outlet's historical bias prior.

### The Five Linguistic Dimensions:

| Dimension | Weight | Mathematical Formulation | Linguistic Rationale |
| :--- | :---: | :--- | :--- |
| **Superlative Density ($S_{sup}$)** | **0.25** | $S_{sup} = \min\left(1.0, \frac{N_{\text{buzz}}}{N_{\text{words}}} \times 35\right)$ | Flags extreme hyperbolic adjectives, parabolic profit targets, and crisis intensifiers (`revolutionary`, `game-changer`, `100x`, `skyrocket`, `bloodbath`). |
| **Sentiment Subjectivity ($S_{subj}$)** | **0.25** | $S_{subj} = \text{TextBlob Subjectivity} \in [0, 1]$ | Quantifies the presence of subjective opinions and emotional adjectives versus matter-of-fact wire reporting. |
| **Clickbait Syntax ($S_{click}$)** | **0.20** | $0.35 C_{\text{caps}} + 0.30 P_{\text{excl}} + 0.25 U_{\text{urg}} + 0.10 Q$ | Captures typographic shouting (ALL-CAPS ratio), exclamation marks (`!`), urgency triggers (`URGENT`, `ALERT`), and rhetorical question traps. |
| **Vague Authority ($S_{vague}$)** | **0.15** | $S_{vague} = \min\left(1.0, N_{\text{vague}} \times 0.45\right)$ | Penalizes speculative claims shielded behind unnamed or unverified sources (`experts warn`, `insiders reveal`, `sources say`, `market whispers`). |
| **Quantitative Grounding ($S_{unsub}$)** | **0.15** | $S_{unsub} = \max\left(0.0, 1.0 - \frac{N_{\text{numeric}}}{N_{\text{words}}} \times 40\right)$ | Measures the absence of empirical validation (dollar amounts, percentages, balance sheet stats, concrete dates) in assertions. |

### Decision Tiers:
- **$0.00 \le H < 0.25$ — Low Hype (Objective / Wire)**: Factual reporting with verified sources and balance sheet figures (e.g., Reuters, Wall Street Journal).
- **$0.25 \le H < 0.50$ — Moderate Buzz**: Standard technology and business feature journalism with measured editorial framing.
- **$0.50 \le H < 0.75$ — High Hype / Sensational**: Elevated emotional tone, speculative price targets, and dramatic phrasing.
- **$0.75 \le H \le 1.00$ — Critical BS / Speculative Frenzy**: Parabolic assertions, conspiratorial urgency, and extreme buzzword density.

---

## 2. Echo-Chamber & Narrative Network Metrics

Implemented in `src/graph.py`, the narrative network models media co-amplification and circular sourcing:

### Narrative Alignment Edge Weight:
Between any two media outlets $A$ and $B$, edge weight $W(A, B)$ combines named entity overlap with content token similarity:

$$W(A, B) = \min\left(1.0, 2.5 \cdot \Big(0.45 \cdot J(E_A, E_B) + 0.55 \cdot \overline{\text{Top}}_k(\text{ItemSim})\Big)\right)$$

- **Entity Jaccard Overlap**: $J(E_A, E_B) = \frac{|E_A \cap E_B|}{|E_A \cup E_B|}$ computes shared coverage of tickers, executives, and organizations.
- **Top-$k$ Item Similarity**: Evaluates cross-outlet article similarity via content n-grams and token overlap.
- **Edge Threshold**: Edges with $W(A, B) < 0.15$ are pruned to eliminate baseline background noise.

### Graph-Theoretic Analytics:
- **PageRank Centrality**: Evaluates which outlets serve as the primary structural epicenters propagating news cycles into mainstream distribution.
- **Betweenness Centrality**: Pinpoints boundary-spanning outlets that bridge speculative communities and traditional institutional press.
- **Greedy Modularity Community Detection**: Discovers structural clusters (e.g., *Speculative Frenzy Cluster*, *Institutional Wire Cluster*, *Enterprise Tech Cluster*) exhibiting intense intra-community narrative repetition.
