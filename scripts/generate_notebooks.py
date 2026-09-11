"""Generator script to produce all 5 Jupyter notebooks using nbformat.

Includes:
- Automatic path and working directory resolution (os.chdir(PROJECT_ROOT))
- Defensive imports for optional/heavy libraries (torch, whisper, spacy)
- Executable cells with no missing dependency hard crashes
"""

from pathlib import Path
import nbformat as nbf

NOTEBOOKS_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
(NOTEBOOKS_DIR / "exploratory").mkdir(parents=True, exist_ok=True)
(NOTEBOOKS_DIR / "reports").mkdir(parents=True, exist_ok=True)

COMMON_PREAMBLE = (
    "# Ensure project root is in sys.path and is current working directory\n"
    "import os\n"
    "import sys\n"
    "from pathlib import Path\n\n"
    "NOTEBOOK_DIR = Path.cwd().resolve()\n"
    "PROJECT_ROOT = NOTEBOOK_DIR.parent if NOTEBOOK_DIR.name == 'notebooks' else NOTEBOOK_DIR\n"
    "if str(PROJECT_ROOT) not in sys.path:\n"
    "    sys.path.insert(0, str(PROJECT_ROOT))\n"
    "os.chdir(PROJECT_ROOT)\n"
    "print(f'[OK] Working directory set to project root: {PROJECT_ROOT}')\n"
)


def make_notebook(cells):
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    nb.metadata.kernelspec = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    }
    nb.metadata.language_info = {
        "name": "python",
        "version": "3.12"
    }
    return nb


def build_nb_00():
    cells = [
        nbf.v4.new_markdown_cell(
            "# 🚀 00 - Environment Setup, Verification & Configuration\n\n"
            "### AI-Powered BS & Hype Analyzer for News & Financial Media\n"
            "**100% Local Inference & Multi-Modal Analysis Stack**\n\n"
            "This notebook verifies the local execution environment, checks dependency integrity, "
            "inspects hardware acceleration availability (CUDA/CPU), and loads pipeline configurations.\n\n"
            "---"
        ),
        nbf.v4.new_code_cell(
            COMMON_PREAMBLE + "\n"
            "# 1. Environment & Core Dependency Verification\n"
            "import platform\n"
            "import pandas as pd\n"
            "import numpy as np\n"
            "import networkx as nx\n"
            "import plotly\n"
            "import textblob\n"
            "import feedparser\n"
            "import pyvis\n\n"
            "# Defensive check for deep learning acceleration (PyTorch)\n"
            "try:\n"
            "    import torch\n"
            "    torch_status = f'v{torch.__version__} (CUDA Available: {torch.cuda.is_available()})'\n"
            "except ImportError:\n"
            "    torch_status = 'Not installed (Optional for live audio transcription; sample audio and full NLP/graph stack 100% active)'\n\n"
            "# Defensive check for whisper & spacy\n"
            "try:\n"
            "    import whisper\n"
            "    whisper_status = 'Installed'\n"
            "except ImportError:\n"
            "    whisper_status = 'Not installed (Optional for live audio transcription)'\n\n"
            "try:\n"
            "    import spacy\n"
            "    spacy_status = f'v{spacy.__version__}'\n"
            "except ImportError:\n"
            "    spacy_status = 'Not installed (Financial regex entity engine active)'\n\n"
            "print('=' * 65)\n"
            "print('  BS & HYPE ANALYZER - SYSTEM DIAGNOSTICS')\n"
            "print('=' * 65)\n"
            "print(f'Python Version:    {sys.version.split()[0]} ({platform.platform()})')\n"
            "print(f'Pandas Version:    {pd.__version__}')\n"
            "print(f'NetworkX Version:  {nx.__version__}')\n"
            "print(f'Plotly Version:    {plotly.__version__}')\n"
            "print(f'Feedparser:        {feedparser.__version__}')\n"
            "print(f'PyVis:             {pyvis.__version__}')\n"
            "print(f'PyTorch:           {torch_status}')\n"
            "print(f'OpenAI Whisper:    {whisper_status}')\n"
            "print(f'spaCy:             {spacy_status}')\n"
            "print('=' * 65)\n"
            "print('[OK] Local analytics environment verified and ready!')"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Load Master Configuration\n\n"
            "The analyzer uses a unified configuration engine (`src.config.get_config`) supporting "
            "declarative YAML settings, media feed sources, and environment variable overrides."
        ),
        nbf.v4.new_code_cell(
            "from src.config import get_config\n\n"
            "cfg = get_config()\n"
            "print(f'Target Whisper Model:     {cfg.whisper_model}')\n"
            "print(f'High-Hype Alert Threshold: {cfg.scoring.min_hype_threshold}')\n"
            "print(f'Echo Graph Edge Threshold: {cfg.echo_chamber.edge_threshold}')\n"
            "print(f'Configured Media Outlets:  {len(cfg.feeds)}')\n\n"
            "print('\\nConfigured Outlets:')\n"
            "for f in cfg.feeds:\n"
            "    print(f'  - [{f.id}] {f.name} ({f.category}) | Bias: {f.bias_label} | Prior Weight: {f.weight}')"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Directory Layout & Data Verification\n\n"
            "Verify that local data stores and reporting output directories are properly initialized."
        ),
        nbf.v4.new_code_cell(
            "from src.config import RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR\n\n"
            "for label, p in [('Raw Data', RAW_DATA_DIR), ('Interim Data', INTERIM_DATA_DIR), \n"
            "                 ('Processed Data', PROCESSED_DATA_DIR), ('Figures', FIGURES_DIR)]:\n"
            "    p.mkdir(parents=True, exist_ok=True)\n"
            "    files = list(p.glob('*.*'))\n"
            "    print(f'{label:15s} [{p}]: {len(files)} files found.')\n\n"
            "print('\\n[OK] Setup complete. Proceed to Notebook 01 for data ingestion!')"
        )
    ]
    return make_notebook(cells)


def build_nb_01():
    cells = [
        nbf.v4.new_markdown_cell(
            "# 📡 01 - Multi-Modal Ingestion: RSS Feeds & YouTube Audio\n\n"
            "### Pipeline Stage 1: Data Ingestion & Normalization\n"
            "This notebook demonstrates our dual-modality ingestion engine:\n"
            "1. **Live and pre-cached RSS feeds** spanning 10 institutional, retail, and tech media outlets.\n"
            "2. **YouTube audio extraction and local Whisper transcription** for financial influencer video content.\n\n"
            "---"
        ),
        nbf.v4.new_code_cell(
            COMMON_PREAMBLE + "\n"
            "import pandas as pd\n"
            "from src.ingest import RSSIngester, YouTubeIngester, ingest_all\n\n"
            "# Ingest sample multimodal dataset (offline reproducible mode)\n"
            "df_raw = ingest_all(use_sample=True)\n"
            "print(f'Total items ingested: {len(df_raw)}')\n"
            "print(f'Modality breakdown:\\n{df_raw[\"source_type\"].value_counts()}')\n"
            "df_raw.head(3)"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Outlet Representation & Volume Analysis\n\n"
            "Let's inspect how articles are distributed across media categories and bias labels."
        ),
        nbf.v4.new_code_cell(
            "outlet_summary = df_raw.groupby(['outlet', 'category', 'bias_label']).size().reset_index(name='article_count')\n"
            "outlet_summary.sort_values(by='article_count', ascending=False)"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Multi-Modal Audio Ingestion: Local Whisper Transcription\n\n"
            "Financial hype frequently spreads via video and podcast channels before hitting print. "
            "Our audio pipeline ingests YouTube audio tracks via `yt-dlp` and generates transcriptions "
            "locally using OpenAI Whisper without sending any data to third-party cloud APIs."
        ),
        nbf.v4.new_code_cell(
            "yt_sample = YouTubeIngester.load_cached_transcript()\n"
            "print(f'Video Title:        {yt_sample[\"title\"]}')\n"
            "print(f'Channel:            {yt_sample[\"channel\"]}')\n"
            "print(f'Speaker:            {yt_sample[\"speaker\"]}')\n"
            "print(f'Local Whisper Model:{yt_sample[\"whisper_model_used\"]}')\n"
            "print(f'Duration:           {yt_sample[\"duration_sec\"]} seconds')\n"
            "print('\\n--- Transcript Excerpt ---')\n"
            "print(yt_sample['full_transcript'][:400] + '...')\n"
            "print('\\n--- First 3 Timestamped Audio Segments ---')\n"
            "for seg in yt_sample['segments'][:3]:\n"
            "    print(f'[{seg[\"start\"]:04.1f}s - {seg[\"end\"]:04.1f}s] {seg[\"text\"]}')"
        ),
        nbf.v4.new_markdown_cell(
            "## 4. Persist Ingested Articles to Interim Cache\n\n"
            "Save raw ingested articles to `data/interim/ingested_articles.csv` for downstream feature extraction."
        ),
        nbf.v4.new_code_cell(
            "from src.config import INTERIM_DATA_DIR\n\n"
            "interim_file = INTERIM_DATA_DIR / 'ingested_articles.csv'\n"
            "df_raw.to_csv(interim_file, index=False)\n"
            "print(f'[OK] Successfully saved {len(df_raw)} records to {interim_file}')\n"
            "print('Proceed to Notebook 02 for feature engineering and hype scoring!')"
        )
    ]
    return make_notebook(cells)


def build_nb_02():
    cells = [
        nbf.v4.new_markdown_cell(
            "# 🔬 02 - Feature Engineering, Linguistic Signals & Hype Scores\n\n"
            "### Mathematical & Linguistic Architecture of the BS & Hype Metric\n\n"
            "Financial and media sensationalism operates across five quantifiable linguistic dimensions:\n\n"
            "1. **Superlative / Buzzword Density ($S_{sup}$)**: Density of hyperbolic intensifiers (`game-changer`, `skyrocket`, `to the moon`, `bloodbath`, `100x`).\n"
            "2. **Sentiment Subjectivity ($S_{subj}$)**: Polarity subjectivity metric ($0.0 = \\text{objective fact}$, $1.0 = \\text{pure opinion}$). \n"
            "3. **Clickbait Syntactic Signals ($S_{click}$)**: Headline all-caps ratio, exclamation intensity, urgency triggers (`urgent warning`, `must watch`).\n"
            "4. **Vague Authority Citations ($S_{vague}$)**: Anonymous assertions without named sources (`experts warn`, `insiders suggest`, `market whispers`).\n"
            "5. **Quantitative Grounding Disparity ($S_{unsub}$)**: Disproportion between qualitative claims and verified empirical stats/currencies/numbers.\n\n"
            "$$\\text{Hype Score} = \\text{clamp}\\Big(\\sum w_i S_i \\cdot (0.8 + 0.2 \\cdot \\Omega_{\\text{outlet}}), 0.0, 1.0\\Big)$$\n\n"
            "---"
        ),
        nbf.v4.new_code_cell(
            COMMON_PREAMBLE + "\n"
            "import pandas as pd\n"
            "from src.config import INTERIM_DATA_DIR, PROCESSED_DATA_DIR\n"
            "from src.features import HypeFeatureExtractor\n"
            "from src.viz import (\n"
            "    plot_hype_distribution,\n"
            "    plot_outlet_comparison,\n"
            "    plot_subjectivity_vs_hype,\n"
            "    plot_hype_dimension_radar\n"
            ")\n\n"
            "# Load ingested data\n"
            "interim_path = INTERIM_DATA_DIR / 'ingested_articles.csv'\n"
            "if not interim_path.exists():\n"
            "    from src.ingest import ingest_all\n"
            "    df_raw = ingest_all(use_sample=True)\n"
            "    df_raw.to_csv(interim_path, index=False)\n"
            "else:\n"
            "    df_raw = pd.read_csv(interim_path)\n\n"
            "# Run Feature Extraction Engine\n"
            "extractor = HypeFeatureExtractor()\n"
            "df_features = extractor.process_dataframe(df_raw)\n\n"
            "print(f'Processed {len(df_features)} media items.')\n"
            "df_features[['title', 'outlet', 'subjectivity_score', 'superlative_density', 'clickbait_syntax', 'hype_score', 'hype_tier']].head(5)"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Hype Score Distribution Across the Media Spectrum\n\n"
            "Let's visualize the composite score distribution and evaluate our decision threshold ($\tau = 0.50$)."
        ),
        nbf.v4.new_code_cell(
            "fig_dist = plot_hype_distribution(df_features, threshold=0.50)\n"
            "fig_dist.show()"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Outlet Comparative Ranking\n\n"
            "Which media outlets and channels exhibit the highest concentration of sensationalism?"
        ),
        nbf.v4.new_code_cell(
            "fig_outlets = plot_outlet_comparison(df_features)\n"
            "fig_outlets.show()"
        ),
        nbf.v4.new_markdown_cell(
            "## 4. 2D Diagnostic: Subjectivity vs. Hype Density\n\n"
            "In this view, bubble size represents syntactic clickbait intensity. Notice how wire services "
            "(Reuters, WSJ, Bloomberg) cluster in the lower left corner (low subjectivity, low hype), "
            "whereas sensational broadcast and crypto influencers dominate the upper right quadrant."
        ),
        nbf.v4.new_code_cell(
            "fig_scatter = plot_subjectivity_vs_hype(df_features)\n"
            "fig_scatter.show()"
        ),
        nbf.v4.new_markdown_cell(
            "## 5. Case Study: 5-Factor Linguistic Diagnostics\n\n"
            "Compare the diagnostic radar fingerprint of the most sensational item vs an objective wire release."
        ),
        nbf.v4.new_code_cell(
            "top_hyped = df_features.sort_values(by='hype_score', ascending=False).iloc[0].to_dict()\n"
            "most_objective = df_features.sort_values(by='hype_score', ascending=True).iloc[0].to_dict()\n\n"
            "fig_radar_hyped = plot_hype_dimension_radar(top_hyped)\n"
            "fig_radar_hyped.show()\n\n"
            "fig_radar_obj = plot_hype_dimension_radar(most_objective)\n"
            "fig_radar_obj.show()"
        ),
        nbf.v4.new_markdown_cell(
            "## 6. Persist Processed Features to Parquet & CSV\n\n"
            "Export processed features to `data/processed/sample_features.parquet` for downstream graph and dashboard use."
        ),
        nbf.v4.new_code_cell(
            "df_features.to_parquet(PROCESSED_DATA_DIR / 'sample_features.parquet', index=False)\n"
            "df_features.to_csv(PROCESSED_DATA_DIR / 'sample_features.csv', index=False)\n"
            "print('[OK] Processed features saved to Parquet and CSV. Proceed to Notebook 03!')"
        )
    ]
    return make_notebook(cells)


def build_nb_03():
    cells = [
        nbf.v4.new_markdown_cell(
            "# 🕸️ 03 - Echo-Chamber Graph & Network Centrality Mapping\n\n"
            "### Uncovering Information Contagion & Amplification Loops\n\n"
            "Sensational financial stories do not exist in a vacuum; they circulate in **echo chambers** "
            "where multiple outlets parrot identical buzzwords, anonymous sources, and tickers without independent verification.\n\n"
            "In this notebook, we model cross-outlet media dynamics as an **attributed undirected network**:\n"
            "- **Nodes**: Media outlets (attributed with average hype, category, and flagged ratio).\n"
            "- **Edges**: Weighted narrative alignment combining Named Entity Jaccard similarity and top article lexical convergence.\n"
            "- **Centrality**: PageRank and Degree Centrality identify the primary **echo epicenters**.\n"
            "- **Modularity**: Greedy modularity community detection partitions the graph into distinct thematic echo chambers.\n\n"
            "---"
        ),
        nbf.v4.new_code_cell(
            COMMON_PREAMBLE + "\n"
            "import pandas as pd\n"
            "import networkx as nx\n"
            "from src.config import PROCESSED_DATA_DIR, FIGURES_DIR\n"
            "from src.graph import EchoChamberGraphBuilder\n"
            "from src.viz import plot_echo_chamber_network_plotly, export_pyvis_network_html, display_html_in_notebook, open_in_browser\n\n"
            "# Load enriched features\n"
            "features_path = PROCESSED_DATA_DIR / 'sample_features.parquet'\n"
            "if features_path.exists():\n"
            "    df = pd.read_parquet(features_path)\n"
            "else:\n"
            "    df = pd.read_csv(PROCESSED_DATA_DIR / 'sample_features.csv')\n\n"
            "# Build Echo-Chamber Graph\n"
            "builder = EchoChamberGraphBuilder()\n"
            "G = builder.build_outlet_graph(df, edge_threshold=0.15)\n\n"
            "print(f'Graph Nodes (Outlets): {len(G.nodes)}')\n"
            "print(f'Graph Edges (Echo Links): {len(G.edges)}')\n\n"
            "summary_data = []\n"
            "for node, data in G.nodes(data=True):\n"
            "    summary_data.append({\n"
            "        'Outlet': node,\n"
            "        'Category': data.get('category'),\n"
            "        'Avg Hype': data.get('avg_hype_score'),\n"
            "        'Community': data.get('community'),\n"
            "        'PageRank': data.get('pagerank'),\n"
            "        'Degree': data.get('degree_centrality')\n"
            "    })\n\n"
            "df_nodes = pd.DataFrame(summary_data).sort_values(by='PageRank', ascending=False)\n"
            "df_nodes"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Interactive Force-Directed Network Graph (Plotly)\n\n"
            "- **Node Color**: Average BS / Hype score (Viridis/Plasma).\n"
            "- **Node Size**: PageRank network influence (how central the outlet is to the broader echo system).\n"
            "- **Hover**: Inspect community clusters, category, and flagged rates."
        ),
        nbf.v4.new_code_cell(
            "fig_network = plot_echo_chamber_network_plotly(G)\n"
            "fig_network.show()"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Detailed Edge Analysis: Shared Narratives & Common Entities\n\n"
            "Examine which outlets form the strongest narrative echo loops and which entities they co-amplify."
        ),
        nbf.v4.new_code_cell(
            "edge_records = []\n"
            "for u, v, d in G.edges(data=True):\n"
            "    edge_records.append({\n"
            "        'Source Outlet': u,\n"
            "        'Target Outlet': v,\n"
            "        'Echo Strength': d.get('weight'),\n"
            "        'Co-Amplified Entities': ', '.join(d.get('common_entities', []))\n"
            "    })\n\n"
            "df_edges = pd.DataFrame(edge_records).sort_values(by='Echo Strength', ascending=False)\n"
            "df_edges.head(10)"
        ),
        nbf.v4.new_markdown_cell(
            "## 4. Physics-Based Interactive PyVis Simulation\n\n"
            "This section exports and renders a real-time ForceAtlas2 physics simulation of the echo chamber.\n\n"
            "> **💡 JupyterLab Desktop Rendering Tip**:\n"
            "> Double-clicking `.html` files in JupyterLab's file sidebar opens their raw code in the text editor, "
            "and right-clicking *HTML Preview* disables JavaScript execution by design for security reasons. \n"
            "> Therefore, the interactive graph is rendered **directly in the notebook output cell below** "
            "using an isolated iframe viewer. You can also click **🌐 Open in External Browser** to manipulate it "
            "in Google Chrome or Microsoft Edge with full GPU hardware acceleration!"
        ),
        nbf.v4.new_code_cell(
            "import ipywidgets as widgets\n"
            "from IPython.display import display\n\n"
            "html_path = export_pyvis_network_html(G, FIGURES_DIR / 'echo_chamber_graph.html')\n"
            "print(f'[OK] PyVis graph exported to: {html_path}')\n\n"
            "# 1. Launch button for external browser (Chrome/Edge/Firefox)\n"
            "launch_btn = widgets.Button(\n"
            "    description='🌐 Open Interactive Simulation in External Browser',\n"
            "    button_style='info',\n"
            "    tooltip='Launch full-screen GPU-accelerated simulation in default browser',\n"
            "    layout=widgets.Layout(width='380px', margin='8px 0')\n"
            ")\n"
            "launch_btn.on_click(lambda _b: open_in_browser(html_path))\n"
            "display(launch_btn)\n\n"
            "# 2. Render directly in notebook cell\n"
            "display(display_html_in_notebook(html_path, height=650))\n"
            "print('\\nProceed to Notebook 04 for the live executive dashboard!')"
        )
    ]
    return make_notebook(cells)


def build_nb_04():
    cells = [
        nbf.v4.new_markdown_cell(
            "## 🎯 Problem & Impact\n\n"
            "Sensationalized financial and technology media routinely distort market reality—using fear-mongering and "
            "speculative euphoria to drive ad revenue and clicks at the expense of investor clarity. The **BS & Hype Analyzer** "
            "counters this information pollution through an auditable 5-factor linguistic metric, an attributed narrative "
            "echo-chamber graph, and an interactive real-time dashboard running 100% locally. Retail investors, risk analysts, "
            "educators, and the public benefit from programmatic noise reduction, pinpointing circular rumor contagion before "
            "making critical investment decisions.\n\n"
            "---"
        ),
        nbf.v4.new_markdown_cell(
            "## ▶ Start Here (Demo Instructions)\n\n"
            "Welcome to the **BS & Hype Analyzer Executive Dashboard**. Follow these quick steps for an optimal demonstration:\n"
            "- **Run all cells from the top**: The notebook runs instantly using precomputed local features (zero network calls or Whisper audio downloads required).\n"
            "- **Use the 'Min hype' slider**: Dynamically filter sensational articles (default is set to **0.25**, the 70th percentile of hype intensity in the sample dataset).\n"
            "- **Toggle outlets to compare hype**: Compare high-hype sources against objective wire baselines (the default view pre-selects the **Contrasting Trio: CNBC vs Reuters vs TechCrunch**).\n"
            "- **Interactive HTML Visualizations**: In JupyterLab Desktop, double-clicking `.html` files opens the text editor and 'HTML Preview' strips JavaScript. Use Section 4 (**Interactive Visuals Hub**) below to inspect all 4 HTML figures directly inside this notebook, or click **Open in External Browser** to view in Chrome/Edge.\n\n"
            "*Note: The default view already renders an engaging, non-empty contrasting subset of media items!*"
        ),

        nbf.v4.new_markdown_cell(
            "# 🎛️ 04 - Interactive Executive Dashboard & Hype Inspector\n\n"
            "### AI-Powered BS & Hype Analyzer — Competition Demo Notebook\n\n"
            "This interactive dashboard allows decision-makers, financial analysts, and researchers to:\n"
            "- **Filter in real-time** by media outlet, sector, and minimum hype threshold.\n"
            "- **Inspect key performance indicators (KPIs)** on information pollution.\n"
            "- **Search by ticker or topic** (`NVIDIA`, `Bitcoin`, `Fed`, `AI`).\n"
            "- **Drill down into individual articles** with a 5-factor linguistic radar breakdown.\n"
            "- **Explore the live narrative echo-chamber network**.\n\n"
            "---"
        ),
        nbf.v4.new_code_cell(
            COMMON_PREAMBLE + "\n"
            "import pandas as pd\n"
            "import ipywidgets as widgets\n"
            "from IPython.display import display, HTML, clear_output\n\n"
            "from src.config import PROCESSED_DATA_DIR\n"
            "from src.graph import EchoChamberGraphBuilder\n"
            "from src.viz import (\n"
            "    plot_hype_distribution,\n"
            "    plot_outlet_comparison,\n"
            "    plot_subjectivity_vs_hype,\n"
            "    plot_echo_chamber_network_plotly,\n"
            "    plot_hype_dimension_radar\n"
            ")\n\n"
            "# 1. Load Precomputed Features\n"
            "features_path = PROCESSED_DATA_DIR / 'sample_features.parquet'\n"
            "if features_path.exists():\n"
            "    df = pd.read_parquet(features_path)\n"
            "else:\n"
            "    df = pd.read_csv(PROCESSED_DATA_DIR / 'sample_features.csv')\n\n"
            "builder = EchoChamberGraphBuilder()\n"
            "G = builder.build_outlet_graph(df)\n"
            "print(f'[OK] Dashboard initialized with {len(df)} articles across {df[\"outlet\"].nunique()} outlets!')"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Live Executive Control Panel & KPI Cards\n\n"
            "Use the interactive controls below to filter data and trigger live analytical updates."
        ),
        nbf.v4.new_code_cell(
            "# UI Controls\n"
            "CONTRASTING_TRIO = 'Contrasting Trio (CNBC, Reuters, TechCrunch)'\n"
            "outlet_options = [CONTRASTING_TRIO, 'All (Full Media Spectrum)'] + sorted(list(df['outlet'].unique()))\n"
            "category_options = ['All'] + sorted(list(df['category'].dropna().unique()))\n\n"
            "outlet_dropdown = widgets.Dropdown(options=outlet_options, value=CONTRASTING_TRIO, description='Outlet Focus:', layout=widgets.Layout(width='340px'))\n"
            "cat_dropdown = widgets.Dropdown(options=category_options, value='All', description='Category:', layout=widgets.Layout(width='280px'))\n"
            "threshold_slider = widgets.FloatSlider(value=0.25, min=0.05, max=0.85, step=0.05, description='Min Hype:', continuous_update=False, layout=widgets.Layout(width='330px'))\n"
            "search_box = widgets.Text(value='', placeholder='Search ticker/keyword (e.g. Nvidia, Bitcoin)...', description='Search:', layout=widgets.Layout(width='350px'))\n\n"
            "controls_row1 = widgets.HBox([outlet_dropdown, cat_dropdown])\n"
            "controls_row2 = widgets.HBox([threshold_slider, search_box])\n\n"
            "out_kpis = widgets.Output()\n"
            "out_charts = widgets.Output()\n"
            "out_drilldown = widgets.Output()\n\n"
            "def update_dashboard(*args):\n"
            "    sub_df = df.copy()\n"
            "    \n"
            "    # Filter by outlet\n"
            "    if outlet_dropdown.value == CONTRASTING_TRIO:\n"
            "        sub_df = sub_df[sub_df['outlet'].isin(['CNBC Markets', 'Reuters Business', 'TechCrunch AI & Startups'])]\n"
            "    elif outlet_dropdown.value != 'All (Full Media Spectrum)':\n"
            "        sub_df = sub_df[sub_df['outlet'] == outlet_dropdown.value]\n"
            "        \n"
            "    # Filter by category\n"
            "    if cat_dropdown.value != 'All':\n"
            "        sub_df = sub_df[sub_df['category'] == cat_dropdown.value]\n"
            "        \n"
            "    # Filter by search keyword\n"
            "    q = search_box.value.strip().lower()\n"
            "    if q:\n"
            "        sub_df = sub_df[sub_df['title'].str.lower().str.contains(q) | sub_df['summary'].str.lower().str.contains(q)]\n"
            "        \n"
            "    thresh = threshold_slider.value\n"
            "    flagged = sub_df[sub_df['hype_score'] >= thresh]\n"
            "    flagged_pct = (len(flagged) / len(sub_df) * 100) if len(sub_df) > 0 else 0.0\n"
            "    avg_hype = sub_df['hype_score'].mean() if len(sub_df) > 0 else 0.0\n"
            "    \n"
            "    with out_kpis:\n"
            "        clear_output(wait=True)\n"
            "        kpi_html = f'''\n"
            "        <div style=\"display: flex; gap: 15px; margin: 15px 0;\">\n"
            "            <div style=\"flex: 1; background: #1e1e2e; padding: 15px; border-radius: 8px; border-left: 5px solid #00CC96;\">\n"
            "                <div style=\"color: #aaa; font-size: 12px;\">TOTAL ANALYZED</div>\n"
            "                <div style=\"font-size: 24px; font-weight: bold; color: #fff;\">{len(sub_df)}</div>\n"
            "            </div>\n"
            "            <div style=\"flex: 1; background: #1e1e2e; padding: 15px; border-radius: 8px; border-left: 5px solid #FF6692;\">\n"
            "                <div style=\"color: #aaa; font-size: 12px;\">HIGH-HYPE FLAGGED</div>\n"
            "                <div style=\"font-size: 24px; font-weight: bold; color: #FF6692;\">{len(flagged)} ({flagged_pct:.1f}%)</div>\n"
            "            </div>\n"
            "            <div style=\"flex: 1; background: #1e1e2e; padding: 15px; border-radius: 8px; border-left: 5px solid #FFA15A;\">\n"
            "                <div style=\"color: #aaa; font-size: 12px;\">MEAN HYPE SCORE</div>\n"
            "                <div style=\"font-size: 24px; font-weight: bold; color: #fff;\">{avg_hype:.3f}</div>\n"
            "            </div>\n"
            "            <div style=\"flex: 1; background: #1e1e2e; padding: 15px; border-radius: 8px; border-left: 5px solid #636EFA;\">\n"
            "                <div style=\"color: #aaa; font-size: 12px;\">ECHO GRAPH NODES</div>\n"
            "                <div style=\"font-size: 24px; font-weight: bold; color: #fff;\">{len(G.nodes)}</div>\n"
            "            </div>\n"
            "        </div>\n"
            "        '''\n"
            "        display(HTML(kpi_html))\n"
            "        \n"
            "    with out_charts:\n"
            "        clear_output(wait=True)\n"
            "        if sub_df.empty:\n"
            "            display(HTML('<p style=\"color: #ff6666;\">No items match the current filter criteria.</p>'))\n"
            "        else:\n"
            "            fig1 = plot_hype_distribution(sub_df, threshold=thresh)\n"
            "            fig1.show()\n"
            "            fig2 = plot_subjectivity_vs_hype(sub_df)\n"
            "            fig2.show()\n\n"
            "    with out_drilldown:\n"
            "        clear_output(wait=True)\n"
            "        if not sub_df.empty:\n"
            "            top_item = sub_df.sort_values(by='hype_score', ascending=False).iloc[0].to_dict()\n"
            "            radar_fig = plot_hype_dimension_radar(top_item)\n"
            "            radar_fig.show()\n"
            "            \n"
            "            drill_html = f'''\n"
            "            <div style=\"background: #181824; padding: 15px; border-radius: 8px; margin-top: 10px;\">\n"
            "                <h4 style=\"color: #FF6692; margin-top: 0;\">⚠️ Highest Hype Item in Selected Scope</h4>\n"
            "                <p><b>Title:</b> {top_item.get('title')}</p>\n"
            "                <p><b>Outlet:</b> {top_item.get('outlet')} | <b>Category:</b> {top_item.get('category')} | <b>Hype Score:</b> {top_item.get('hype_score'):.3f}</p>\n"
            "                <p><b>Summary:</b> {top_item.get('summary')}</p>\n"
            "            </div>\n"
            "            '''\n"
            "            display(HTML(drill_html))\n\n"
            "outlet_dropdown.observe(update_dashboard, names='value')\n"
            "cat_dropdown.observe(update_dashboard, names='value')\n"
            "threshold_slider.observe(update_dashboard, names='value')\n"
            "search_box.observe(update_dashboard, names='value')\n\n"
            "# Render Dashboard\n"
            "display(widgets.VBox([controls_row1, controls_row2, out_kpis, out_charts, out_drilldown]))\n"
            "update_dashboard()"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Narrative Echo-Chamber Graph Exploration\n\n"
            "Inspect the interactive network showing cross-outlet echo loops."
        ),
        nbf.v4.new_code_cell(
            "fig_net = plot_echo_chamber_network_plotly(G)\n"
            "fig_net.show()"
        ),
        nbf.v4.new_markdown_cell(
            "## 4. Interactive Visuals Hub & Standalone HTML Explorer\n\n"
            "Explore all 4 competition visualizations directly inside JupyterLab Desktop using the dropdown below, "
            "or click **Open in External Browser** to launch them in your default browser (Chrome/Edge) at full screen."
        ),
        nbf.v4.new_code_cell(
            "from src.viz import create_html_viewer_widget\n"
            "display(create_html_viewer_widget())"
        ),
        nbf.v4.new_markdown_cell(
            "## 5. Key Findings, Business Narrative & Decision Context\n\n"
            "### Executive Summary\n"
            "1. **Bimodal Information Landscape**: Financial media exhibits a sharp bimodal distribution. "
            "Institutional wire services (Reuters, WSJ, Bloomberg) cluster at hype scores below 0.25, while "
            "retail trading bullet points and crypto social channels spike above 0.75.\n"
            "2. **Echo Chamber Transmission**: High-hype narratives consistently originate in social/video channels "
            "before being amplified by retail financial broadcasters (CNBC, MarketWatch), which act as transmission "
            "bridges with the highest network PageRank and betweenness centrality.\n"
            "3. **Decision Impact**: Using the configurable threshold $\\tau=0.50$, quantitative hedge funds and "
            "corporate risk analysts can programmatically filter noise, discount sensational rumors, and prevent "
            "FOMO-driven algorithmic trades."
        )
    ]
    return make_notebook(cells)


if __name__ == "__main__":
    nbf.write(build_nb_00(), str(NOTEBOOKS_DIR / "00_setup_and_imports.ipynb"))
    nbf.write(build_nb_01(), str(NOTEBOOKS_DIR / "01_ingest_rss_and_youtube.ipynb"))
    nbf.write(build_nb_02(), str(NOTEBOOKS_DIR / "02_feature_engineering_and_hype_scores.ipynb"))
    nbf.write(build_nb_03(), str(NOTEBOOKS_DIR / "03_echo_chamber_graph.ipynb"))
    nbf.write(build_nb_04(), str(NOTEBOOKS_DIR / "04_interactive_dashboard.ipynb"))
    print("[OK] Successfully generated all 5 Jupyter notebooks in notebooks/")
