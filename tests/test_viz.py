"""Unit tests for visualization components and HTML exports in src/viz.py."""

from unittest.mock import patch
import networkx as nx
import pandas as pd
import pytest
from IPython.display import HTML

from src.viz import (
    display_html_in_notebook,
    export_pyvis_network_html,
    open_in_browser,
    plot_echo_chamber_network_plotly,
    plot_hype_dimension_radar,
    plot_hype_distribution,
    plot_outlet_comparison,
    plot_subjectivity_vs_hype,
)


@pytest.fixture
def sample_viz_df() -> pd.DataFrame:
    """Fixture returning sample media DataFrame for visualization tests."""
    return pd.DataFrame([
        {
            "id": "1",
            "outlet": "CNBC Markets",
            "title": "Shocking AI Surge",
            "summary": "AI chip rally reaches boiling point.",
            "category": "Financial Media",
            "hype_score": 0.65,
            "hype_tier": "High Hype / Sensational",
            "is_flagged": True,
            "subjectivity_score": 0.75,
            "clickbait_syntax": 0.8,
            "superlative_density": 0.5,
            "vague_authority_score": 0.4,
            "unsubstantiated_score": 0.6,
        },
        {
            "id": "2",
            "outlet": "Reuters Business",
            "title": "Treasury Yields Stable",
            "summary": "Bond yields held steady following morning data release.",
            "category": "Macro & Markets",
            "hype_score": 0.12,
            "hype_tier": "Low Hype (Objective / Wire)",
            "is_flagged": False,
            "subjectivity_score": 0.20,
            "clickbait_syntax": 0.0,
            "superlative_density": 0.0,
            "vague_authority_score": 0.1,
            "unsubstantiated_score": 0.1,
        },
    ])


@pytest.fixture
def sample_viz_graph() -> nx.Graph:
    """Fixture returning a 2-node sample attributed graph."""
    G = nx.Graph()
    G.add_node("CNBC Markets", avg_hype_score=0.65, category="Financial Media", pagerank=0.35, flagged_percentage=60.0)
    G.add_node("Reuters Business", avg_hype_score=0.12, category="Macro & Markets", pagerank=0.15, flagged_percentage=0.0)
    G.add_edge("CNBC Markets", "Reuters Business", weight=0.45)
    return G


def test_export_pyvis_network_html_self_contained(sample_viz_graph: nx.Graph, tmp_path) -> None:
    """Verify PyVis exports fully inlined, self-contained HTML without relative lib dependencies."""
    out_file = tmp_path / "test_pyvis.html"
    exported_path = export_pyvis_network_html(sample_viz_graph, out_file)

    assert exported_path.exists()
    assert exported_path.stat().st_size > 50000  # Self-contained JS bundled

    content = exported_path.read_text(encoding="utf-8")
    assert "CNBC Markets" in content
    assert "Reuters Business" in content
    # Ensure no relative path to lib/bindings
    assert "lib/bindings" not in content
    # Ensure vis-network script is present
    assert "vis-network" in content


def test_display_html_in_notebook(tmp_path) -> None:
    """Verify display_html_in_notebook produces valid script-enabled iframe HTML object."""
    html_file = tmp_path / "sample.html"
    html_file.write_text("<html><body><h1>Test Visualization</h1></body></html>", encoding="utf-8")

    display_obj = display_html_in_notebook(html_file, height=500)
    assert isinstance(display_obj, HTML)
    assert "iframe srcdoc=" in display_obj.data
    assert "height: 500px;" in display_obj.data
    assert "sandbox=" in display_obj.data
    assert "allow-scripts" in display_obj.data


def test_open_in_browser(tmp_path) -> None:
    """Verify open_in_browser calls system browser on existing files and handles missing files gracefully."""
    dummy_file = tmp_path / "exists.html"
    dummy_file.write_text("<h1>Hello</h1>", encoding="utf-8")

    with patch("webbrowser.open", return_value=True) as mock_open:
        assert open_in_browser(dummy_file) is True
        mock_open.assert_called_once()

    missing_file = tmp_path / "does_not_exist.html"
    assert open_in_browser(missing_file) is False


def test_plotly_figures_render(sample_viz_df: pd.DataFrame, sample_viz_graph: nx.Graph) -> None:
    """Verify all Plotly visualization functions generate valid go.Figure objects."""
    fig_dist = plot_hype_distribution(sample_viz_df)
    assert fig_dist.data is not None

    fig_out = plot_outlet_comparison(sample_viz_df)
    assert fig_out.data is not None

    fig_scat = plot_subjectivity_vs_hype(sample_viz_df)
    assert fig_scat.data is not None

    fig_net = plot_echo_chamber_network_plotly(sample_viz_graph)
    assert fig_net.data is not None

    fig_radar = plot_hype_dimension_radar(sample_viz_df.iloc[0].to_dict())
    assert fig_radar.data is not None
