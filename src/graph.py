"""Echo-chamber network analysis and narrative graph mapping.

Models information propagation, thematic repetition, and outlet echo chambers:
- Lexical & Named Entity Jaccard similarity metrics
- Cross-outlet narrative alignment graph construction
- Community detection (Louvain / greedy modularity)
- Centrality metrics (PageRank, Degree, Betweenness)
- Interactive PyVis and Plotly graph generation
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
from networkx.algorithms import community
import pandas as pd

from src.config import EchoChamberSettings, get_config

logger = logging.getLogger(__name__)


def compute_jaccard(set_a: Set[str], set_b: Set[str]) -> float:
    """Compute Jaccard similarity between two sets.

    Args:
        set_a: First set of tokens or entities.
        set_b: Second set of tokens or entities.

    Returns:
        Float in [0.0, 1.0].
    """
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    if union == 0:
        return 0.0
    return float(round(intersection / union, 4))


def extract_content_tokens(text: str) -> Set[str]:
    """Extract filtered content words (lowercase alphanumeric, length > 3).

    Args:
        text: Input string.

    Returns:
        Set of clean tokens.
    """
    if not text:
        return set()
    stopwords = {
        "the",
        "and",
        "for",
        "are",
        "was",
        "its",
        "not",
        "this",
        "that",
        "with",
        "from",
        "about",
        "after",
        "before",
        "their",
        "which",
        "would",
        "could",
        "should",
        "will",
        "have",
        "were",
        "been",
        "more",
        "when",
        "what",
        "said",
        "says",
        "also",
        "into",
        "over",
        "than",
        "them",
        "then",
        "some",
        "very",
    }
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return {w for w in words if w not in stopwords}


def parse_entities(raw: Any) -> Set[str]:
    """Safely parse entity representations from string, list, or array into a set.

    Args:
        raw: Raw entity data in list, ndarray, or serialized string format.

    Returns:
        Set of clean uppercase entity strings.
    """
    import ast

    if isinstance(raw, (list, set, tuple)):
        return {str(x).strip().upper() for x in raw if str(x).strip()}
    if hasattr(raw, "tolist"):
        return {str(x).strip().upper() for x in raw.tolist() if str(x).strip()}
    if isinstance(raw, str):
        clean = raw.strip()
        if clean.startswith("[") and clean.endswith("]"):
            try:
                parsed = ast.literal_eval(clean)
                if isinstance(parsed, (list, tuple, set)):
                    return {str(x).strip().upper() for x in parsed if str(x).strip()}
            except Exception:
                pass
        return {
            x.strip(" '\"[]").upper()
            for x in clean.split(",")
            if len(x.strip(" '\"[]")) > 1
        }
    return set()


class EchoChamberGraphBuilder:
    """Constructs and analyzes media narrative echo chambers."""

    def __init__(self, settings: Optional[EchoChamberSettings] = None):
        """Initialize graph builder.

        Args:
            settings: EchoChamberSettings. Defaults to app config.
        """
        cfg = get_config()
        self.settings = settings or cfg.echo_chamber

    def compute_item_similarity(
        self,
        item_a: Dict[str, Any],
        item_b: Dict[str, Any],
    ) -> float:
        """Compute hybrid similarity between two media items.

        Combines entity overlap (weight 0.6) with lexical word overlap (weight 0.4).

        Args:
            item_a: First item dictionary.
            item_b: Second item dictionary.

        Returns:
            Hybrid similarity score in [0.0, 1.0].
        """
        entities_a = parse_entities(item_a.get("entities", []))
        entities_b = parse_entities(item_b.get("entities", []))
        entity_sim = compute_jaccard(entities_a, entities_b)

        tokens_a = extract_content_tokens(
            f"{item_a.get('title', '')} {item_a.get('summary', '')}"
        )
        tokens_b = extract_content_tokens(
            f"{item_b.get('title', '')} {item_b.get('summary', '')}"
        )
        lexical_sim = compute_jaccard(tokens_a, tokens_b)

        sim = 0.60 * entity_sim + 0.40 * lexical_sim
        return float(round(sim, 4))

    def build_outlet_graph(
        self,
        df: pd.DataFrame,
        edge_threshold: Optional[float] = None,
    ) -> nx.Graph:
        """Build an outlet-level echo-chamber graph from article features.

        Nodes represent media outlets with attributes:
        - avg_hype_score
        - article_count
        - category
        - bias_label

        Edges represent narrative and entity convergence between outlets.

        Args:
            df: DataFrame of articles with computed features.
            edge_threshold: Minimum edge weight to retain. Defaults to config.

    Returns:
            NetworkX undirected Graph with node and edge attributes.
        """
        threshold = (
            edge_threshold
            if edge_threshold is not None
            else self.settings.edge_threshold
        )
        G = nx.Graph()

        if df.empty:
            return G

        # Group articles by outlet
        outlets = df["outlet"].unique()
        outlet_items: Dict[str, List[Dict[str, Any]]] = {}

        for outlet in outlets:
            sub_df = df[df["outlet"] == outlet]
            outlet_items[outlet] = sub_df.to_dict(orient="records")

            avg_hype = float(round(sub_df["hype_score"].mean(), 3))
            flagged_pct = float(
                round((sub_df["is_flagged"].sum() / len(sub_df)) * 100, 1)
            )
            cat = sub_df["category"].iloc[0] if "category" in sub_df.columns else "General"
            bias = (
                sub_df["bias_label"].iloc[0]
                if "bias_label" in sub_df.columns
                else "Neutral"
            )

            G.add_node(
                outlet,
                outlet_name=outlet,
                article_count=len(sub_df),
                avg_hype_score=avg_hype,
                flagged_percentage=flagged_pct,
                category=cat,
                bias_label=bias,
            )

        # Compute pairwise outlet echo alignment
        outlet_list = list(outlets)
        for i in range(len(outlet_list)):
            for j in range(i + 1, len(outlet_list)):
                o1 = outlet_list[i]
                o2 = outlet_list[j]
                items1 = outlet_items[o1]
                items2 = outlet_items[o2]

                # Aggregate outlet entities
                e1 = set().union(*[parse_entities(a.get("entities", [])) for a in items1])
                e2 = set().union(*[parse_entities(a.get("entities", [])) for a in items2])
                common_entities = e1.intersection(e2)
                agg_entity_sim = compute_jaccard(e1, e2)

                sim_scores = []
                for a1 in items1:
                    for a2 in items2:
                        s = self.compute_item_similarity(a1, a2)
                        if s > 0:
                            sim_scores.append(s)

                top_n = min(5, len(sim_scores)) if sim_scores else 0
                sim_scores.sort(reverse=True)
                top_pair_sim = sum(sim_scores[:top_n]) / top_n if top_n > 0 else 0.0

                # Calibrated composite echo strength
                raw_echo = 0.45 * agg_entity_sim + 0.55 * top_pair_sim
                echo_strength = float(round(min(1.0, raw_echo * 2.5), 4))

                if echo_strength >= threshold:
                    G.add_edge(
                        o1,
                        o2,
                        weight=echo_strength,
                        common_entities=list(common_entities)[:6],
                    )

        # Compute centrality metrics
        if len(G) > 0:
            deg_centrality = nx.degree_centrality(G)
            pageranks = nx.pagerank(G, weight="weight") if len(G.edges) > 0 else deg_centrality
            betweenness = (
                nx.betweenness_centrality(G, weight="weight")
                if len(G.edges) > 0
                else deg_centrality
            )

            # Community detection
            try:
                communities = community.greedy_modularity_communities(G, weight="weight")
                community_map = {}
                for comm_id, comm_nodes in enumerate(communities):
                    for node in comm_nodes:
                        community_map[node] = comm_id
            except Exception:
                community_map = {node: 0 for node in G.nodes()}

            for node in G.nodes():
                G.nodes[node]["degree_centrality"] = round(deg_centrality.get(node, 0.0), 3)
                G.nodes[node]["pagerank"] = round(pageranks.get(node, 0.0), 3)
                G.nodes[node]["betweenness"] = round(betweenness.get(node, 0.0), 3)
                G.nodes[node]["community"] = community_map.get(node, 0)

        return G

    def build_article_graph(
        self,
        df: pd.DataFrame,
        edge_threshold: Optional[float] = None,
        max_articles: int = 60,
    ) -> nx.Graph:
        """Build fine-grained article-level narrative citation graph.

        Args:
            df: DataFrame containing enriched articles.
            edge_threshold: Minimum similarity threshold.
            max_articles: Capped article count for performance and readability.

        Returns:
            NetworkX Graph where nodes are articles.
        """
        threshold = (
            edge_threshold
            if edge_threshold is not None
            else self.settings.edge_threshold
        )
        G = nx.Graph()

        sample_df = df.head(max_articles)
        records = sample_df.to_dict(orient="records")

        for r in records:
            G.add_node(
                r["id"],
                title=r["title"],
                outlet=r["outlet"],
                hype_score=r["hype_score"],
                hype_tier=r["hype_tier"],
                category=r.get("category", "General"),
                entities=r.get("entities", []),
            )

        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                sim = self.compute_item_similarity(records[i], records[j])
                if sim >= threshold:
                    G.add_edge(
                        records[i]["id"],
                        records[j]["id"],
                        weight=sim,
                    )

        return G
