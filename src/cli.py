"""Command-line interface (CLI) for BS & Hype Analyzer.

Executes end-to-end ingestion, NLP feature extraction, echo-chamber graph modeling,
and instant single-text diagnostics directly from the terminal.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import (
    FIGURES_DIR,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    REPORTS_DIR,
    get_config,
)
from src.features import HypeFeatureExtractor
from src.graph import EchoChamberGraphBuilder
from src.ingest import RSSIngester, ingest_all
from src.viz import (
    export_pyvis_network_html,
    plot_echo_chamber_network_plotly,
    plot_hype_distribution,
    plot_outlet_comparison,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bs_hype_analyzer")


def cmd_ingest(args: argparse.Namespace) -> None:
    """Execute ingestion command."""
    logger.info("Starting ingestion pipeline (use_sample=%s)...", args.use_sample)
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)

    df = ingest_all(use_sample=args.use_sample)
    logger.info("Ingested %d articles/transcripts across %d outlets.", len(df), df["outlet"].nunique() if not df.empty else 0)

    out_csv = INTERIM_DATA_DIR / "ingested_articles.csv"
    df.to_csv(out_csv, index=False)
    logger.info("Saved interim ingested dataset to %s", out_csv)


def cmd_features(args: argparse.Namespace) -> None:
    """Execute feature engineering and hype scoring command."""
    logger.info("Computing NLP hype features and composite scores...")
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    in_csv = INTERIM_DATA_DIR / "ingested_articles.csv"
    if not in_csv.exists():
        logger.info("Interim data not found, running sample ingestion first...")
        df = ingest_all(use_sample=True)
    else:
        df = pd.read_csv(in_csv)

    extractor = HypeFeatureExtractor()
    enriched_df = extractor.process_dataframe(df)

    out_parquet = PROCESSED_DATA_DIR / "sample_features.parquet"
    out_csv = PROCESSED_DATA_DIR / "sample_features.csv"

    try:
        enriched_df.to_parquet(out_parquet, index=False)
        logger.info("Saved processed features to Parquet: %s", out_parquet)
    except Exception as e:
        logger.warning("Could not write Parquet (%s), skipping Parquet export.", e)

    enriched_df.to_csv(out_csv, index=False)
    logger.info("Saved processed features to CSV: %s", out_csv)

    # Print summary statistics
    flagged = enriched_df["is_flagged"].sum()
    pct = (flagged / len(enriched_df)) * 100 if len(enriched_df) > 0 else 0
    logger.info(
        "Feature summary: %d total items, %d flagged high-hype (%.1f%%). Mean hype: %.3f",
        len(enriched_df),
        flagged,
        pct,
        enriched_df["hype_score"].mean(),
    )


def cmd_graph(args: argparse.Namespace) -> None:
    """Build and export echo-chamber graph."""
    logger.info("Constructing narrative echo-chamber graph...")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    features_csv = PROCESSED_DATA_DIR / "sample_features.csv"
    features_parquet = PROCESSED_DATA_DIR / "sample_features.parquet"

    if features_parquet.exists():
        df = pd.read_parquet(features_parquet)
    elif features_csv.exists():
        df = pd.read_csv(features_csv)
    else:
        logger.info("Features not found, extracting now...")
        df_raw = ingest_all(use_sample=True)
        extractor = HypeFeatureExtractor()
        df = extractor.process_dataframe(df_raw)

    builder = EchoChamberGraphBuilder()
    edge_thresh = args.edge_threshold if args.edge_threshold is not None else builder.settings.edge_threshold
    G = builder.build_outlet_graph(df, edge_threshold=edge_thresh)

    logger.info("Echo-Chamber Graph constructed: %d nodes, %d edges.", len(G.nodes), len(G.edges))

    # Export PyVis HTML
    html_path = FIGURES_DIR / "echo_chamber_graph.html"
    export_pyvis_network_html(G, html_path)
    logger.info("Exported interactive network to %s", html_path)

    # Export Plotly HTML figures
    fig_net = plot_echo_chamber_network_plotly(G)
    fig_net.write_html(str(FIGURES_DIR / "network_plotly.html"))

    fig_dist = plot_hype_distribution(df)
    fig_dist.write_html(str(FIGURES_DIR / "hype_distribution.html"))

    fig_out = plot_outlet_comparison(df)
    fig_out.write_html(str(FIGURES_DIR / "outlet_comparison.html"))

    logger.info("Saved interactive Plotly visual figures to %s", FIGURES_DIR)


def cmd_analyze(args: argparse.Namespace) -> None:
    """Analyze arbitrary text on the fly."""
    extractor = HypeFeatureExtractor()
    item = {
        "title": args.title or "Ad-hoc User Submission",
        "summary": args.text,
        "outlet_weight": 1.0,
    }
    result = extractor.analyze_item(item)

    print("\n" + "=" * 60)
    print("  BS & HYPE ANALYZER - INSTANT DIAGNOSTIC")
    print("=" * 60)
    print(f"Title:                  {result['title']}")
    print(f"Composite Hype Score:   {result['hype_score']:.3f} / 1.000")
    print(f"Hype Classification:    {result['hype_tier']}")
    print(f"High Hype Flagged:      {'[!] YES (HIGH HYPE)' if result['is_flagged'] else '[OK] NO (NORMAL)'}")
    print("-" * 60)
    print("Linguistic Dimensions:")
    print(f"  - Superlative / Buzzword Density:  {result['superlative_density']:.3f}")
    print(f"  - Sentiment Subjectivity:          {result['subjectivity_score']:.3f}")
    print(f"  - Clickbait Syntax Signals:        {result['clickbait_syntax']:.3f}")
    print(f"  - Vague Anonymous Citations:       {result['vague_authority_score']:.3f}")
    print(f"  - Unsubstantiated Claims Penalty:  {result['unsubstantiated_score']:.3f}")
    print(f"Named Entities Identified ({result['ner_count']}): {', '.join(result['entities'][:8])}")
    print("=" * 60 + "\n")


def cmd_run_demo(args: argparse.Namespace) -> None:
    """Execute high-speed offline demo initialization using sample data."""
    logger.info("Initializing demo using cached sample data (no live network/audio calls)...")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    features_parquet = PROCESSED_DATA_DIR / "sample_features.parquet"
    features_csv = PROCESSED_DATA_DIR / "sample_features.csv"

    if features_parquet.exists():
        df = pd.read_parquet(features_parquet)
    elif features_csv.exists():
        df = pd.read_csv(features_csv)
    else:
        logger.info("Precomputed features not found, extracting from sample data...")
        df_raw = ingest_all(use_sample=True)
        extractor = HypeFeatureExtractor()
        df = extractor.process_dataframe(df_raw)
        try:
            df.to_parquet(features_parquet, index=False)
        except Exception:
            pass
        df.to_csv(features_csv, index=False)

    html_path = FIGURES_DIR / "echo_chamber_graph.html"
    builder = EchoChamberGraphBuilder()
    G = builder.build_outlet_graph(df)

    if not html_path.exists():
        export_pyvis_network_html(G, html_path)
        logger.info("Exported PyVis graph to %s", html_path)

    # Export Plotly HTML figures if missing
    plotly_html = FIGURES_DIR / "network_plotly.html"
    if not plotly_html.exists():
        fig_net = plot_echo_chamber_network_plotly(G)
        fig_net.write_html(str(plotly_html))

    flagged = df["is_flagged"].sum() if "is_flagged" in df.columns else 0
    pct = (flagged / len(df)) * 100 if len(df) > 0 else 0
    mean_hype = df["hype_score"].mean() if "hype_score" in df.columns else 0.0

    print("\n" + "=" * 65)
    print("  AI-POWERED BS & HYPE ANALYZER - DEMO READY")
    print("=" * 65)
    print(f"Total Media Articles & Transcripts: {len(df)}")
    print(f"Distinct Media Outlets Tracked:     {df['outlet'].nunique() if 'outlet' in df.columns else 0}")
    print(f"High-Hype Items Flagged (>= 0.50):  {flagged} ({pct:.1f}%)")
    print(f"Mean Hype Score Across Sample:      {mean_hype:.3f} / 1.000")
    print(f"Echo-Chamber Graph Nodes:           {len(G.nodes)} outlets")
    print(f"Echo-Chamber Graph Edges:           {len(G.edges)} narrative links")
    print(f"Interactive Network File:           {html_path}")
    print("-" * 65)
    print("Demo ready: open notebooks/04_interactive_dashboard.ipynb in JupyterLab Desktop.")
def cmd_view(args: argparse.Namespace) -> None:
    """Open generated interactive HTML visualizations in default web browser."""
    from src.viz import open_in_browser

    files = {
        "echo_chamber_graph.html": FIGURES_DIR / "echo_chamber_graph.html",
        "network_plotly.html": FIGURES_DIR / "network_plotly.html",
        "hype_distribution.html": FIGURES_DIR / "hype_distribution.html",
        "outlet_comparison.html": FIGURES_DIR / "outlet_comparison.html",
    }

    target_name = args.file
    if target_name == "all":
        print("Opening all generated visualizations in default web browser...")
        for name, p in files.items():
            if p.exists():
                print(f"  [>] Opening {name}...")
                open_in_browser(p)
            else:
                print(f"  [!] {name} not found. Run 'python -m src.cli run_demo' first.")
        return

    target_path = files.get(target_name)
    if not target_path or not target_path.exists():
        candidate = Path(target_name)
        if candidate.exists():
            target_path = candidate
        else:
            candidate2 = FIGURES_DIR / target_name
            if candidate2.exists():
                target_path = candidate2
            else:
                print(f"[!] File not found: {target_name}. Run 'python -m src.cli run_demo' first.")
                sys.exit(1)

    print(f"[OK] Opening {target_path.name} in system default browser...")
    open_in_browser(target_path)


def build_parser() -> argparse.ArgumentParser:

    """Construct CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="bs-hype-analyzer",
        description="AI-Powered BS & Hype Analyzer for News & Financial Media",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Ingest
    ingest_p = subparsers.add_parser("ingest", help="Ingest media feeds & transcripts")
    ingest_p.add_argument(
        "--use-sample",
        "--sample",
        action="store_true",
        default=True,
        dest="use_sample",
        help="Use local pre-cached sample dataset",
    )
    ingest_p.add_argument(
        "--live",
        action="store_false",
        dest="use_sample",
        help="Fetch live RSS feeds over HTTP",
    )

    # Features
    features_p = subparsers.add_parser("features", help="Compute NLP features and hype scores")
    features_p.add_argument(
        "--sample",
        action="store_true",
        default=True,
        help="Use sample dataset for feature extraction",
    )

    # Graph
    graph_p = subparsers.add_parser("graph", help="Build echo-chamber network graph")
    graph_p.add_argument(
        "--sample",
        action="store_true",
        default=True,
        help="Use sample dataset for graph modeling",
    )
    graph_p.add_argument(
        "--edge-threshold",
        type=float,
        default=None,
        help="Minimum edge similarity threshold (default from config: 0.15)",
    )

    # Run Demo
    demo_p = subparsers.add_parser("run_demo", help="Prepare and verify offline demo artifacts")
    demo_p.add_argument(
        "--sample",
        action="store_true",
        default=True,
        help="Use precomputed sample dataset for instant demo initialization",
    )

    # Analyze
    analyze_p = subparsers.add_parser("analyze", help="Analyze arbitrary text")
    analyze_p.add_argument("--text", type=str, required=True, help="Text to analyze")
    analyze_p.add_argument("--title", type=str, default="", help="Optional title")

    # View
    view_p = subparsers.add_parser("view", help="Open interactive HTML visualizations in your default web browser")
    view_p.add_argument(
        "--file",
        type=str,
        default="echo_chamber_graph.html",
        help="HTML figure to view: echo_chamber_graph.html (default), network_plotly.html, hype_distribution.html, outlet_comparison.html, or 'all'",
    )

    return parser


def main() -> None:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "ingest": cmd_ingest,
        "features": cmd_features,
        "graph": cmd_graph,
        "run_demo": cmd_run_demo,
        "analyze": cmd_analyze,
        "view": cmd_view,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
