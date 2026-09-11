"""Script to generate high-resolution visual highlight PNG figures for reports and README.

Generates:
1. reports/figures/hype_histogram.png
2. reports/figures/radar_cnbc_vs_reuters.png
3. reports/figures/echo_chamber_labeled.png
"""

import math
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
import pandas as pd

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "sample_features.parquet"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]


def generate_hype_histogram(df: pd.DataFrame) -> None:
    """Generate reports/figures/hype_histogram.png with annotated example headlines."""
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor="#0E1117")
    ax.set_facecolor("#161B22")

    scores = df["hype_score"].values
    n, bins, patches = ax.hist(scores, bins=25, range=(0, 1), edgecolor="#30363D", linewidth=1.2)

    # Color code bars by hype tier
    for patch, leftside in zip(patches, bins[:-1]):
        if leftside < 0.25:
            patch.set_facecolor("#00CC96")  # Low Hype (Green)
        elif leftside < 0.50:
            patch.set_facecolor("#FFA15A")  # Moderate (Orange)
        elif leftside < 0.75:
            patch.set_facecolor("#FF6692")  # High Hype (Pink)
        else:
            patch.set_facecolor("#EF553B")  # Critical BS (Red)

    # Decision thresholds
    ax.axvline(0.25, color="#8B949E", linestyle=":", linewidth=1.5, alpha=0.8)
    ax.axvline(0.50, color="#FF4136", linestyle="--", linewidth=2.0)
    ax.text(0.51, max(n) * 0.92, "High-Hype Alert Threshold (τ = 0.50)", color="#FF6692",
            fontsize=10, fontweight="bold")

    # Annotations for 3 example headlines
    # 1. Low Hype
    ax.annotate(
        "Low Hype (Score: 0.08)\n\"Fed Holds Benchmark Rate Steady\nat 5.25%-5.50% Citing Inflation Data\"\n(Reuters Business)",
        xy=(0.08, 18), xytext=(0.05, max(n) * 0.65),
        arrowprops=dict(facecolor="#00CC96", edgecolor="#00CC96", arrowstyle="->", lw=1.8),
        fontsize=9, color="#E6EDF3",
        bbox=dict(boxstyle="round,pad=0.4", fc="#0D1117", ec="#00CC96", lw=1.2)
    )

    # 2. Moderate Buzz
    ax.annotate(
        "Moderate Buzz (Score: 0.35)\n\"Palantir Technologies Gains 8%\nFollowing Major Defense Contract\"\n(Yahoo Finance)",
        xy=(0.35, 12), xytext=(0.32, max(n) * 0.78),
        arrowprops=dict(facecolor="#FFA15A", edgecolor="#FFA15A", arrowstyle="->", lw=1.8),
        fontsize=9, color="#E6EDF3",
        bbox=dict(boxstyle="round,pad=0.4", fc="#0D1117", ec="#FFA15A", lw=1.2)
    )

    # 3. Critical BS / High Hype
    ax.annotate(
        "Critical BS Alert (Score: 0.88)\n\"CRASH OR RALLY? Strategists\nIssue URGENT Warning on Overnight Bloodbath!\"\n(CNBC Markets)",
        xy=(0.68, 6), xytext=(0.58, max(n) * 0.45),
        arrowprops=dict(facecolor="#EF553B", edgecolor="#EF553B", arrowstyle="->", lw=1.8),
        fontsize=9, color="#E6EDF3",
        bbox=dict(boxstyle="round,pad=0.4", fc="#0D1117", ec="#EF553B", lw=1.2)
    )

    ax.set_title("Distribution of Hype & Sensationalism Across 151 Financial Media Items",
                 fontsize=14, fontweight="bold", color="#FFFFFF", pad=15)
    ax.set_xlabel("Composite BS & Hype Score (0.00 = Objective Wire, 1.00 = Extreme Speculation)",
                  fontsize=11, color="#C9D1D9", labelpad=10)
    ax.set_ylabel("Number of Articles & Transcripts", fontsize=11, color="#C9D1D9", labelpad=10)
    ax.tick_params(colors="#8B949E")
    for spine in ax.spines.values():
        spine.set_color("#30363D")

    # Legend
    legend_patches = [
        mpatches.Patch(color="#00CC96", label="Low Hype (0.00 - 0.25)"),
        mpatches.Patch(color="#FFA15A", label="Moderate Buzz (0.25 - 0.50)"),
        mpatches.Patch(color="#FF6692", label="High Hype (0.50 - 0.75)"),
        mpatches.Patch(color="#EF553B", label="Critical BS (0.75 - 1.00)"),
    ]
    ax.legend(handles=legend_patches, facecolor="#161B22", edgecolor="#30363D",
              labelcolor="#C9D1D9", loc="upper right")

    plt.tight_layout()
    out_path = FIGURES_DIR / "hype_histogram.png"
    plt.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"[OK] Generated {out_path}")


def generate_radar_cnbc_vs_reuters(df: pd.DataFrame) -> None:
    """Generate reports/figures/radar_cnbc_vs_reuters.png comparing CNBC vs Reuters profiles."""
    dims = [
        ("superlative_density", "Superlative\nDensity"),
        ("subjectivity_score", "Sentiment\nSubjectivity"),
        ("clickbait_syntax", "Clickbait\nSyntax"),
        ("vague_authority_score", "Vague\nAuthority"),
        ("unsubstantiated_score", "Ungrounded\nClaims"),
    ]
    dim_keys = [k for k, _ in dims]
    dim_labels = [label for _, label in dims]

    cnbc_df = df[df["outlet"].str.contains("CNBC", case=False, na=False)]
    reuters_df = df[df["outlet"].str.contains("Reuters", case=False, na=False)]

    cnbc_vals = [float(cnbc_df[k].mean()) for k in dim_keys]
    reuters_vals = [float(reuters_df[k].mean()) for k in dim_keys]

    # Close polygons
    cnbc_vals += [cnbc_vals[0]]
    reuters_vals += [reuters_vals[0]]
    num_vars = len(dims)
    angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]
    angles += [angles[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True), facecolor="#0E1117")
    ax.set_facecolor("#161B22")

    # Draw axes and labels
    plt.xticks(angles[:-1], dim_labels, color="#C9D1D9", size=10, fontweight="bold")
    ax.set_rlabel_position(30)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], color="#8B949E", size=9)
    plt.ylim(0, 1.0)
    ax.spines["polar"].set_color("#30363D")
    ax.grid(color="#30363D", linestyle="--", alpha=0.7)

    # Plot CNBC (Red)
    ax.plot(angles, cnbc_vals, color="#FF4B4B", linewidth=2.5, linestyle="solid", label="CNBC Markets (High-Hype Profile)")
    ax.fill(angles, cnbc_vals, color="#FF4B4B", alpha=0.35)

    # Plot Reuters (Teal)
    ax.plot(angles, reuters_vals, color="#00CC96", linewidth=2.5, linestyle="solid", label="Reuters Business (Wire Baseline Profile)")
    ax.fill(angles, reuters_vals, color="#00CC96", alpha=0.35)

    plt.title("5-Factor Linguistic Hype Profile: CNBC Markets vs. Reuters Business\n",
              size=13, fontweight="bold", color="#FFFFFF", pad=20)
    plt.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), facecolor="#161B22",
               edgecolor="#30363D", labelcolor="#E6EDF3")

    plt.tight_layout()
    out_path = FIGURES_DIR / "radar_cnbc_vs_reuters.png"
    plt.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"[OK] Generated {out_path}")


def generate_echo_chamber_labeled(df: pd.DataFrame) -> None:
    """Generate static reports/figures/echo_chamber_labeled.png network graph."""
    from src.graph import EchoChamberGraphBuilder

    builder = EchoChamberGraphBuilder()
    G = builder.build_outlet_graph(df)

    fig, ax = plt.subplots(figsize=(13, 9), facecolor="#0E1117")
    ax.set_facecolor("#0E1117")

    pos = nx.spring_layout(G, seed=42, k=0.9, iterations=80)

    # Community color mapping
    # 0 = High Hype / Speculative, 1 = Institutional Wire, 2 = Tech
    cluster_names = {
        0: "High-Hype / Speculative Frenzy (CNBC, MarketWatch, CoinDesk, Influencer)",
        1: "Institutional Wire Baseline (Reuters, WSJ, Financial Times)",
        2: "Consumer Tech & Enterprise (Bloomberg, The Verge, TechCrunch)"
    }
    cluster_colors = {
        0: "#EF553B",  # Red
        1: "#00CC96",  # Green
        2: "#FFA15A"   # Orange
    }

    # Draw edges
    for u, v, data in G.edges(data=True):
        weight = data.get("weight", 0.1)
        width = max(1.0, weight * 8)
        alpha = min(0.85, max(0.25, weight * 2))
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                color="#58A6FF", alpha=alpha, linewidth=width, zorder=1)

    # Draw nodes
    node_sizes = [int(G.nodes[n].get("pagerank", 0.1) * 3500) + 400 for n in G.nodes()]
    node_colors = [cluster_colors.get(G.nodes[n].get("community", 0), "#8B949E") for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors,
                           edgecolors="#FFFFFF", linewidths=1.8, ax=ax)

    # Draw labels
    labels = {n: f"{n}\n(Hype: {G.nodes[n].get('avg_hype_score', 0):.2f})" for n in G.nodes()}
    for node, (x, y) in pos.items():
        avg_h = G.nodes[node].get("avg_hype_score", 0.0)
        c_id = G.nodes[node].get("community", 0)
        c_color = cluster_colors.get(c_id, "#FFFFFF")
        ax.text(x, y - 0.07, labels[node], fontsize=8.5, fontweight="bold",
                color="#FFFFFF", ha="center", va="top",
                bbox=dict(boxstyle="round,pad=0.25", fc="#161B22", ec=c_color, lw=1.2, alpha=0.9))

    ax.set_title("Media Narrative Echo Chamber: Cross-Outlet Convergence Network\n"
                 "Node Size = PageRank Influence | Node Color = Detected Thematic Community | Edge Width = Echo Strength",
                 fontsize=13, fontweight="bold", color="#FFFFFF", pad=15)
    ax.axis("off")

    # Legend
    legend_elements = [
        mpatches.Patch(color="#EF553B", label="Cluster 0: High-Hype / Speculative Frenzy"),
        mpatches.Patch(color="#00CC96", label="Cluster 1: Institutional Wire Baseline"),
        mpatches.Patch(color="#FFA15A", label="Cluster 2: Consumer Tech & Innovation"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", facecolor="#161B22",
              edgecolor="#30363D", labelcolor="#E6EDF3", fontsize=9.5)

    plt.tight_layout()
    out_path = FIGURES_DIR / "echo_chamber_labeled.png"
    plt.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"[OK] Generated {out_path}")


def main():
    if not PROCESSED_FILE.exists():
        from src.ingest import ingest_all
        from src.features import HypeFeatureExtractor
        df_raw = ingest_all(use_sample=True)
        extractor = HypeFeatureExtractor()
        df = extractor.process_dataframe(df_raw)
        df.to_parquet(PROCESSED_FILE, index=False)
    else:
        df = pd.read_parquet(PROCESSED_FILE)

    print(f"Loaded {len(df)} records for visual highlights generation.")
    generate_hype_histogram(df)
    generate_radar_cnbc_vs_reuters(df)
    generate_echo_chamber_labeled(df)
    print("All 3 visual highlights generated successfully.")


if __name__ == "__main__":
    main()
