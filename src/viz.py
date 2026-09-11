"""Interactive visualization components using Plotly and PyVis.

Generates competition-grade visual storytelling artifacts:
- Hype score distributions with decision thresholds
- Cross-outlet comparative box plots and bar charts
- Multi-dimensional subjectivity vs hype scatter analysis
- Interactive force-directed Echo-Chamber graph in Plotly & PyVis
- Single-item 5-factor diagnostic radar charts
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import FIGURES_DIR

logger = logging.getLogger(__name__)

COLOR_MAP_TIERS = {
    "Low Hype (Objective / Wire)": "#00CC96",
    "Moderate Buzz": "#FFA15A",
    "High Hype / Sensational": "#FF6692",
    "Critical BS / Speculative Frenzy": "#EF553B",
}


def plot_hype_distribution(
    df: pd.DataFrame, threshold: float = 0.50
) -> go.Figure:
    """Create interactive histogram of hype score distribution with threshold line.

    Args:
        df: DataFrame with 'hype_score' and 'hype_tier'.
        threshold: Decision threshold for high-hype classification.

    Returns:
        Plotly Figure object.
    """
    fig = px.histogram(
        df,
        x="hype_score",
        color="hype_tier",
        nbins=25,
        marginal="box",
        title="<b>Information Pollution Spectrum: Distribution of Hype Scores</b>",
        labels={"hype_score": "Composite Hype / BS Score (0.0 to 1.0)", "count": "Article Count"},
        color_discrete_map=COLOR_MAP_TIERS,
        opacity=0.85,
        template="plotly_dark",
    )

    fig.add_vline(
        x=threshold,
        line_width=3,
        line_dash="dash",
        line_color="#FF3366",
        annotation_text=f"High Hype Threshold ({threshold:.2f})",
        annotation_position="top right",
    )

    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=12),
        legend_title_text="Hype Classification",
        bargap=0.08,
        height=480,
    )
    return fig


def plot_outlet_comparison(df: pd.DataFrame) -> go.Figure:
    """Plot comparative horizontal ranking of outlets by average hype.

    Args:
        df: DataFrame containing 'outlet' and 'hype_score'.

    Returns:
        Plotly Figure object.
    """
    outlet_stats = (
        df.groupby("outlet")
        .agg(
            avg_hype=("hype_score", "mean"),
            flagged_pct=("is_flagged", lambda x: (x.sum() / len(x)) * 100),
            article_count=("id", "count"),
            category=("category", "first"),
        )
        .reset_index()
        .sort_values(by="avg_hype", ascending=True)
    )

    fig = px.bar(
        outlet_stats,
        x="avg_hype",
        y="outlet",
        color="avg_hype",
        orientation="h",
        color_continuous_scale="Plasma",
        title="<b>Media Outlets Ranked by Average BS / Hype Intensity</b>",
        labels={"avg_hype": "Mean Hype Score", "outlet": "Media Outlet"},
        hover_data={"flagged_pct": ":.1f%", "article_count": True, "category": True},
        template="plotly_dark",
    )

    fig.add_vline(x=0.50, line_dash="dot", line_color="#FF4136", annotation_text="Critical Alert Line")
    fig.update_layout(height=520, coloraxis_showscale=False)
    return fig


def plot_subjectivity_vs_hype(df: pd.DataFrame) -> go.Figure:
    """2D scatter showing relation between linguistic subjectivity and composite hype.

    Args:
        df: DataFrame with 'subjectivity_score', 'hype_score', 'outlet', 'title'.

    Returns:
        Plotly Figure object.
    """
    fig = px.scatter(
        df,
        x="subjectivity_score",
        y="hype_score",
        color="hype_tier",
        size="clickbait_syntax",
        hover_name="title",
        hover_data={
            "outlet": True,
            "hype_score": ":.3f",
            "subjectivity_score": ":.3f",
            "clickbait_syntax": ":.2f",
        },
        title="<b>Subjectivity vs. Hype Density (Bubble Size = Clickbait Syntax)</b>",
        labels={
            "subjectivity_score": "Text Subjectivity (0.0 = Fact, 1.0 = Pure Opinion)",
            "hype_score": "Composite BS / Hype Score",
        },
        color_discrete_map=COLOR_MAP_TIERS,
        template="plotly_dark",
    )
    fig.update_layout(height=520)
    return fig


def plot_echo_chamber_network_plotly(G: nx.Graph) -> go.Figure:
    """Render interactive 2D force-directed Echo Chamber network in Plotly.

    Args:
        G: NetworkX graph of outlets or articles.

    Returns:
        Plotly Figure with interactive nodes and weighted edges.
    """
    if len(G) == 0:
        fig = go.Figure()
        fig.update_layout(title="Echo Chamber Graph (Empty)")
        return fig

    pos = nx.spring_layout(G, seed=42, k=0.7)

    # Edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color="#555577"),
        hoverinfo="none",
        mode="lines",
    )

    # Node traces
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []

    for node, data in G.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        name = data.get("outlet_name", node)
        avg_h = data.get("avg_hype_score", 0.0)
        comm = data.get("community", 0)
        pr = data.get("pagerank", 0.1)
        cat = data.get("category", "")
        flagged = data.get("flagged_percentage", 0.0)

        node_text.append(
            f"<b>{name}</b><br>"
            f"Category: {cat}<br>"
            f"Avg Hype: {avg_h:.3f}<br>"
            f"High-Hype Articles: {flagged:.1f}%<br>"
            f"Echo Community: #{comm}<br>"
            f"PageRank Influence: {pr:.3f}"
        )
        node_color.append(avg_h)
        node_size.append(max(20, min(50, int(pr * 250) + 15)))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        text=[data.get("outlet_name", node) for node, data in G.nodes(data=True)],
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale="Viridis",
            reversescale=False,
            color=node_color,
            size=node_size,
            colorbar=dict(
                thickness=15,
                title=dict(text="Avg Hype Score", side="right"),
                xanchor="left",
            ),
            line_width=2,
            line_color="#FFFFFF",
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="<b>Media Narrative Echo Chamber: Cross-Outlet Convergence Graph</b><br><sup>Edges indicate narrative / entity co-occurrence; Node color reflects average hype; Size indicates network influence (PageRank)</sup>",
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=60),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            template="plotly_dark",
            height=600,
        ),
    )
    return fig


def export_pyvis_network_html(
    G: nx.Graph,
    output_path: Optional[Path] = None,
) -> Path:
    """Export physics-based interactive PyVis HTML network graph.

    Ensures all JS and CSS dependencies are fully inlined (self-contained) and
    written with UTF-8 encoding so it functions offline and inside sandboxed
    iframes without missing relative path errors.

    Args:
        G: NetworkX graph.
        output_path: Target HTML file path. Defaults to reports/figures/echo_chamber_graph.html.

    Returns:
        Path to saved HTML file.
    """
    from pyvis.network import Network

    target = output_path or (FIGURES_DIR / "echo_chamber_graph.html")
    target.parent.mkdir(parents=True, exist_ok=True)

    net = Network(
        height="650px",
        width="100%",
        bgcolor="#111118",
        font_color="#FFFFFF",
        notebook=False,
        cdn_resources="in_line",
    )

    for node, data in G.nodes(data=True):
        avg_h = data.get("avg_hype_score", 0.0)
        color = "#EF553B" if avg_h >= 0.50 else ("#FFA15A" if avg_h >= 0.35 else "#00CC96")
        title_hover = (
            f"{node}\nCategory: {data.get('category', '')}\n"
            f"Avg Hype: {avg_h}\nPageRank: {data.get('pagerank', 0.0)}"
        )
        size = int(data.get("pagerank", 0.1) * 120) + 15
        net.add_node(node, label=node, title=title_hover, color=color, size=size)

    for u, v, data in G.edges(data=True):
        weight = data.get("weight", 0.1)
        net.add_edge(u, v, value=weight, title=f"Narrative Similarity: {weight:.2f}")

    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {"iterations": 150}
      }
    }
    """)

    # Note: net.save_graph crashes on Windows with UnicodeEncodeError in cp1252
    # because pyvis does not pass encoding='utf-8'. We generate HTML and write with utf-8 explicitly.
    html_content = net.generate_html()
    target.write_text(html_content, encoding="utf-8")
    return target


def display_html_in_notebook(
    html_path_or_content: Any,
    height: int = 650,
    width: str = "100%",
) -> Any:
    """Display an HTML file or HTML string inside an isolated, script-enabled iframe.

    Works seamlessly in JupyterLab Desktop, Jupyter Notebook, and exported reports
    without server routing issues or CSP script blocking.

    Args:
        html_path_or_content: Path to the HTML file or raw HTML string.
        height: Iframe height in pixels.
        width: Iframe width (default '100%').

    Returns:
        IPython.display.HTML object containing the embedded iframe.
    """
    import html as html_lib
    import warnings
    from IPython.display import HTML

    path = Path(html_path_or_content)
    if path.is_file():
        raw_html = path.read_text(encoding="utf-8")
    else:
        raw_html = str(html_path_or_content)

    escaped = html_lib.escape(raw_html, quote=True)
    iframe_code = (
        f'<iframe srcdoc="{escaped}" '
        f'style="width: {width}; height: {height}px; border: 1px solid #2e3440; '
        f'border-radius: 8px; background: #111118;" '
        f'sandbox="allow-scripts allow-same-origin allow-popups"></iframe>'
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return HTML(iframe_code)


def open_in_browser(html_path: Any) -> bool:
    """Open an HTML file directly in the system default web browser.

    Args:
        html_path: Path to HTML file.

    Returns:
        True if launched successfully, False otherwise.
    """
    import webbrowser

    p = Path(html_path).resolve()
    if not p.exists():
        logger.warning("HTML file not found: %s", p)
        return False
    return webbrowser.open(p.as_uri())


def create_html_viewer_widget(
    initial_file: str = "echo_chamber_graph.html",
) -> Any:
    """Create an interactive ipywidget selector for viewing generated HTML reports.

    Provides dropdown switching between generated visualizations and a 1-click
    button to launch in the system's default web browser.
    """
    import ipywidgets as widgets
    from IPython.display import clear_output, display

    available_files = {
        "Echo Chamber Network (PyVis Physics)": FIGURES_DIR / "echo_chamber_graph.html",
        "Echo Chamber Network (Plotly 2D)": FIGURES_DIR / "network_plotly.html",
        "Hype Score Distribution": FIGURES_DIR / "hype_distribution.html",
        "Media Outlets Ranking": FIGURES_DIR / "outlet_comparison.html",
    }

    file_dropdown = widgets.Dropdown(
        options=list(available_files.keys()),
        value="Echo Chamber Network (PyVis Physics)" if "Echo Chamber Network (PyVis Physics)" in available_files else list(available_files.keys())[0],
        description="Visualization:",
        layout=widgets.Layout(width="380px"),
    )

    btn_browser = widgets.Button(
        description="Open in External Browser",
        button_style="info",
        tooltip="Open current visualization in Chrome/Edge/Firefox",
        icon="external-link",
        layout=widgets.Layout(width="220px"),
    )

    viewer_output = widgets.Output()

    def render_selected() -> None:
        selected_name = file_dropdown.value
        path = available_files.get(selected_name)
        with viewer_output:
            clear_output(wait=True)
            if path and path.exists():
                display(display_html_in_notebook(path, height=650))
            else:
                display(widgets.HTML(f"<p style='color:#EF553B;'>File not found yet: {path}. Run pipeline or cli to generate.</p>"))

    def on_dropdown_change(change: Any) -> None:
        if change.get("type") == "change" and change.get("name") == "value":
            render_selected()

    def on_button_click(_b: Any) -> None:
        selected_name = file_dropdown.value
        path = available_files.get(selected_name)
        if path and path.exists():
            open_in_browser(path)

    file_dropdown.observe(on_dropdown_change)
    btn_browser.on_click(on_button_click)

    controls = widgets.HBox([file_dropdown, btn_browser], layout=widgets.Layout(margin="10px 0"))
    render_selected()
    return widgets.VBox([controls, viewer_output])



def plot_hype_dimension_radar(row: Dict[str, Any]) -> go.Figure:
    """Create a 5-dimension radar diagnostic chart for a single article or video.

    Args:
        row: Analyzed media item dictionary.

    Returns:
        Plotly polar Radar figure.
    """
    categories = [
        "Superlative Density",
        "Subjectivity",
        "Clickbait Syntax",
        "Vague Authority",
        "Unsubstantiated Claims",
    ]
    values = [
        row.get("superlative_density", 0.0),
        row.get("subjectivity_score", 0.0),
        row.get("clickbait_syntax", 0.0),
        row.get("vague_authority_score", 0.0),
        row.get("unsubstantiated_score", 0.0),
    ]
    # Close polygon
    values.append(values[0])
    categories.append(categories[0])

    title = row.get("title", "Article")
    if len(title) > 60:
        title = title[:57] + "..."

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(239, 85, 59, 0.4)",
            line=dict(color="#EF553B", width=2),
            name="Hype Breakdown",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),
            bgcolor="#1A1B26",
        ),
        showlegend=False,
        title=f"<b>Linguistic Hype Diagnostics</b><br><sup>{title} (Score: {row.get('hype_score', 0):.2f})</sup>",
        template="plotly_dark",
        height=450,
    )
    return fig
