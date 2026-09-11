"""Script to generate assets/architecture.png."""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = ASSETS_DIR / "architecture.png"

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(16, 9), facecolor="#0E1117")
    ax.set_facecolor("#0E1117")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")

    # Title
    ax.text(8, 8.4, "AI-Powered BS & Hype Analyzer — System Architecture", 
            fontsize=20, fontweight="bold", color="#FFFFFF", ha="center")
    ax.text(8, 8.0, "100% Local Inference | Multi-Modal (Text + Audio) | Graph Echo-Chambers | Real-Time Dashboard", 
            fontsize=11, color="#8B949E", ha="center")

    # Stage Box Styles
    box_style_1 = dict(boxstyle="round,pad=0.6,rounding_size=0.3", fc="#161B22", ec="#58A6FF", lw=2)
    box_style_2 = dict(boxstyle="round,pad=0.6,rounding_size=0.3", fc="#161B22", ec="#7EE787", lw=2)
    box_style_3 = dict(boxstyle="round,pad=0.6,rounding_size=0.3", fc="#161B22", ec="#FFA657", lw=2)
    box_style_4 = dict(boxstyle="round,pad=0.6,rounding_size=0.3", fc="#161B22", ec="#D2A8FF", lw=2)

    # Column 1: Ingestion
    ax.text(2.2, 7.1, "1. INGESTION ENGINE", fontsize=12, fontweight="bold", color="#58A6FF", ha="center")
    ax.text(2.2, 5.6, "RSS News Ingestor\n• 10 Outlets (Wire, Fin, Tech)\n• BeautifulSoup HTML Cleaning\n• Title & Summary Extraction\n(feedparser, requests)",
            fontsize=9.5, color="#C9D1D9", ha="center", va="center", bbox=box_style_1)
    ax.text(2.2, 3.2, "YouTube Audio Ingestor\n• yt-dlp Audio Stream Extraction\n• 100% Local OpenAI Whisper\n• Word & Chunk Timestamps\n(yt-dlp, whisper, torch)",
            fontsize=9.5, color="#C9D1D9", ha="center", va="center", bbox=box_style_1)
    ax.text(2.2, 1.4, "Local Storage\n• data/raw/ (Cached JSON)\n• data/interim/ (Parsed CSV)",
            fontsize=9, color="#8B949E", ha="center", va="center", bbox=dict(boxstyle="square,pad=0.4", fc="#0D1117", ec="#30363D", lw=1))

    # Column 2: NLP Features
    ax.text(6.1, 7.1, "2. NLP FEATURE SCORING", fontsize=12, fontweight="bold", color="#7EE787", ha="center")
    ax.text(6.1, 5.7, "Linguistic & Syntactic Signals\n• Superlative / Buzzword Density\n• Sentiment Subjectivity\n• Clickbait Syntax & Caps Ratio\n(TextBlob, Regex, Lexicon)",
            fontsize=9.5, color="#C9D1D9", ha="center", va="center", bbox=box_style_2)
    ax.text(6.1, 3.3, "Grounding & Entity Engine\n• Vague Authority Extraction\n• Empirical Disparity Score\n• NER & Stock/Crypto Tickers\n(spaCy / Financial Lexicon)",
            fontsize=9.5, color="#C9D1D9", ha="center", va="center", bbox=box_style_2)
    ax.text(6.1, 1.4, "Composite Hype Score\n• Weighted Multi-Factor Formula\n• Continuous [0.0, 1.0] Score\n• 4 Categorical Alert Tiers",
            fontsize=9, color="#7EE787", ha="center", va="center", bbox=dict(boxstyle="square,pad=0.4", fc="#0D1117", ec="#238636", lw=1.5))

    # Column 3: Graph Engine
    ax.text(10.0, 7.1, "3. ECHO-CHAMBER GRAPH", fontsize=12, fontweight="bold", color="#FFA657", ha="center")
    ax.text(10.0, 5.7, "Narrative Alignment\n• Entity Jaccard Similarity\n• Lexical N-Gram Overlap\n• Pairwise Outlet Echo Links\n(Jaccard, NetworkX)",
            fontsize=9.5, color="#C9D1D9", ha="center", va="center", bbox=box_style_3)
    ax.text(10.0, 3.3, "Graph Centrality & Clusters\n• PageRank (Echo Epicenters)\n• Betweenness Centrality\n• Modularity Communities\n(networkx.algorithms.community)",
            fontsize=9.5, color="#C9D1D9", ha="center", va="center", bbox=box_style_3)
    ax.text(10.0, 1.4, "Processed Parquet\n• data/processed/sample_features\n• Full Metadata & Graph GraphML",
            fontsize=9, color="#8B949E", ha="center", va="center", bbox=dict(boxstyle="square,pad=0.4", fc="#0D1117", ec="#30363D", lw=1))

    # Column 4: Presentation & UI
    ax.text(13.8, 7.1, "4. DASHBOARD & UI", fontsize=12, fontweight="bold", color="#D2A8FF", ha="center")
    ax.text(13.8, 5.7, "Interactive Visualizations\n• Hype Spectrum Histograms\n• Subjectivity vs Hype Scatter\n• 5-Factor Radar Fingerprints\n(Plotly Dark Theme)",
            fontsize=9.5, color="#C9D1D9", ha="center", va="center", bbox=box_style_4)
    ax.text(13.8, 3.3, "Physics & App Interfaces\n• Force-Directed Network (Plotly)\n• PyVis Physics HTML Graphs\n• ipywidgets Live Dashboard\n(JupyterLab Desktop / CLI)",
            fontsize=9.5, color="#C9D1D9", ha="center", va="center", bbox=box_style_4)
    ax.text(13.8, 1.4, "Decision Deliverable\n• Noise Reduction for Quants\n• Real-Time Risk Disclaimers",
            fontsize=9, color="#D2A8FF", ha="center", va="center", bbox=dict(boxstyle="square,pad=0.4", fc="#0D1117", ec="#8957E5", lw=1.5))

    # Flow Arrows
    arrow_props = dict(arrowstyle="->,head_width=0.4,head_length=0.5", color="#58A6FF", lw=2.5)
    ax.annotate("", xy=(4.2, 5.6), xytext=(3.9, 5.6), arrowprops=arrow_props)
    ax.annotate("", xy=(4.2, 3.2), xytext=(3.9, 3.2), arrowprops=arrow_props)
    ax.annotate("", xy=(8.1, 5.7), xytext=(7.8, 5.7), arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.5", color="#7EE787", lw=2.5))
    ax.annotate("", xy=(8.1, 3.3), xytext=(7.8, 3.3), arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.5", color="#7EE787", lw=2.5))
    ax.annotate("", xy=(12.0, 5.7), xytext=(11.7, 5.7), arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.5", color="#FFA657", lw=2.5))
    ax.annotate("", xy=(12.0, 3.3), xytext=(11.7, 3.3), arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.5", color="#FFA657", lw=2.5))

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"[OK] Generated architecture diagram at {OUT_PATH}")

if __name__ == "__main__":
    create_architecture_diagram()
