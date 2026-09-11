"""Unit tests for network graph builder and echo-chamber detection in src/graph.py."""

import networkx as nx
import pandas as pd
import pytest

from src.graph import (
    EchoChamberGraphBuilder,
    compute_jaccard,
    extract_content_tokens,
    parse_entities,
)


def test_compute_jaccard() -> None:
    """Test Jaccard similarity computation across identical, disjoint, and partial sets."""
    assert compute_jaccard(set(), {"A", "B"}) == 0.0
    assert compute_jaccard({"A", "B"}, set()) == 0.0
    assert compute_jaccard({"A", "B"}, {"A", "B"}) == 1.0
    assert compute_jaccard({"A", "B"}, {"B", "C"}) == pytest.approx(1 / 3, 0.01)
    assert compute_jaccard({"A", "B"}, {"C", "D"}) == 0.0


def test_parse_entities() -> None:
    """Test robust entity parsing from lists, sets, and serialized string formats."""
    assert parse_entities(["Nvidia", "Apple"]) == {"NVIDIA", "APPLE"}
    assert parse_entities("['Nvidia', 'Apple']") == {"NVIDIA", "APPLE"}
    assert parse_entities("Nvidia, Apple") == {"NVIDIA", "APPLE"}
    assert parse_entities(None) == set()


def test_extract_content_tokens() -> None:
    """Test text tokenization and stopword removal."""
    text = "The Federal Reserve will announce the interest rate decision today."
    tokens = extract_content_tokens(text)
    assert "federal" in tokens
    assert "reserve" in tokens
    assert "decision" in tokens
    assert "the" not in tokens
    assert "will" not in tokens


def test_compute_item_similarity() -> None:
    """Test pairwise hybrid item similarity calculation."""
    builder = EchoChamberGraphBuilder()

    item_a = {
        "title": "Nvidia Announces Revolutionary AI Chip With Record Performance",
        "summary": "Nvidia unveiled its newest GPU architecture for cloud servers.",
        "entities": ["NVIDIA", "GPU", "AI"],
    }
    item_b = {
        "title": "Nvidia Next-Gen AI Silicon Ships to Cloud Hyperscalers",
        "summary": "Nvidia confirmed shipments of advanced GPU processors to data centers.",
        "entities": ["NVIDIA", "GPU", "AI"],
    }
    item_c = {
        "title": "Wheat Harvest Forecast Revised Upward Following Favorable Rainfall",
        "summary": "Agricultural yields across the Midwest rose 4% this harvest season.",
        "entities": ["MIDWEST", "USDA"],
    }

    sim_ab = builder.compute_item_similarity(item_a, item_b)
    sim_ac = builder.compute_item_similarity(item_a, item_c)

    assert sim_ab > 0.30, f"Expected high similarity between related tech articles, got {sim_ab}"
    assert sim_ac < 0.10, f"Expected low similarity between unrelated articles, got {sim_ac}"


def test_build_outlet_graph_edge_threshold() -> None:
    """Test that edge_threshold correctly filters edges in the outlet echo-chamber graph."""
    builder = EchoChamberGraphBuilder()

    df = pd.DataFrame(
        [
            {
                "id": "1",
                "outlet": "Outlet A",
                "title": "Bitcoin Skyrockets to New Highs",
                "summary": "Bitcoin and crypto assets surge on institutional ETF inflows.",
                "entities": ["BITCOIN", "CRYPTO", "SOLANA"],
                "hype_score": 0.85,
                "is_flagged": True,
                "category": "Crypto",
                "bias_label": "Speculative",
            },
            {
                "id": "2",
                "outlet": "Outlet B",
                "title": "Bitcoin Rally Continues Unabated",
                "summary": "Bitcoin reaches record prices as ETF demand accelerates.",
                "entities": ["BITCOIN", "ETHEREUM", "BINANCE"],
                "hype_score": 0.80,
                "is_flagged": True,
                "category": "Crypto",
                "bias_label": "Speculative",
            },
            {
                "id": "3",
                "outlet": "Outlet C",
                "title": "Soybean Exports Rise in Port of New Orleans",
                "summary": "Grain shipments to South America expanded 2% in July.",
                "entities": ["NEW ORLEANS", "USDA"],
                "hype_score": 0.15,
                "is_flagged": False,
                "category": "Agriculture",
                "bias_label": "Wire",
            },
        ]
    )

    # Moderate threshold should retain edge between A and B
    g_low = builder.build_outlet_graph(df, edge_threshold=0.15)
    assert g_low.has_edge("Outlet A", "Outlet B")
    assert not g_low.has_edge("Outlet A", "Outlet C")

    # High threshold should filter out edge between A and B
    g_high = builder.build_outlet_graph(df, edge_threshold=0.85)
    assert len(g_high.edges) == 0


def test_graph_centrality_and_communities() -> None:
    """Test computation of PageRank, degree centrality, and community detection."""
    builder = EchoChamberGraphBuilder()

    # Create dummy graph with 4 nodes
    G = nx.Graph()
    G.add_edge("A", "B", weight=0.5)
    G.add_edge("B", "C", weight=0.5)
    G.add_edge("C", "A", weight=0.5)
    G.add_edge("C", "D", weight=0.2)

    deg = nx.degree_centrality(G)
    pr = nx.pagerank(G, weight="weight")

    assert len(deg) == 4
    assert len(pr) == 4
    assert pr["C"] > pr["D"]
