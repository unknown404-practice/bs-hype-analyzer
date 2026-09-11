"""Configuration loader and environment settings for BS & Hype Analyzer.

This module provides structured access to yaml and json configuration files,
supporting environment variable overrides for local model parameters, edge
thresholds, and pipeline switches.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

# Base project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


@dataclass
class FeedConfig:
    """Represents a single RSS feed source."""

    id: str
    name: str
    category: str
    url: str
    bias_label: str
    weight: float = 1.0


@dataclass
class HypeWeights:
    """Weights applied across NLP hype metric dimensions."""

    superlative_density: float = 0.25
    subjectivity_score: float = 0.25
    clickbait_syntax: float = 0.20
    vague_authority: float = 0.15
    unsubstantiated_claims: float = 0.15


@dataclass
class HypeScoringSettings:
    """NLP scoring thresholds and lexicons."""

    min_hype_threshold: float = 0.50
    weights: HypeWeights = field(default_factory=HypeWeights)
    buzzwords: List[str] = field(default_factory=list)
    vague_authorities: List[str] = field(default_factory=list)


@dataclass
class EchoChamberSettings:
    """Graph construction parameters for echo-chamber detection."""

    edge_threshold: float = 0.15
    similarity_metric: str = "hybrid"
    min_community_size: int = 2
    node_size_metric: str = "hype_score"
    layout_algorithm: str = "spring"


@dataclass
class PipelineConfig:
    """Master configuration container for BS & Hype Analyzer."""

    whisper_model: str = "small"
    feeds_json_path: Path = CONFIG_DIR / "feeds.json"
    hype_config_path: Path = CONFIG_DIR / "hype_config.yaml"
    scoring: HypeScoringSettings = field(default_factory=HypeScoringSettings)
    echo_chamber: EchoChamberSettings = field(default_factory=EchoChamberSettings)
    feeds: List[FeedConfig] = field(default_factory=list)


def load_yaml_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML config. Defaults to config/hype_config.yaml.

    Returns:
        Dictionary containing parsed YAML configuration.
    """
    path = config_path or (CONFIG_DIR / "hype_config.yaml")
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_feeds_config(feeds_path: Optional[Path] = None) -> List[FeedConfig]:
    """Load media feeds configuration from JSON.

    Args:
        feeds_path: Path to feeds JSON file. Defaults to config/feeds.json.

    Returns:
        List of FeedConfig objects.
    """
    env_feeds = os.getenv("RSS_FEEDS_JSON")
    path = Path(env_feeds) if env_feeds else (feeds_path or (CONFIG_DIR / "feeds.json"))
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    feeds = []
    for item in data.get("feeds", []):
        feeds.append(
            FeedConfig(
                id=item["id"],
                name=item["name"],
                category=item.get("category", "General"),
                url=item["url"],
                bias_label=item.get("bias_label", "Neutral"),
                weight=float(item.get("weight", 1.0)),
            )
        )
    return feeds


def get_config() -> PipelineConfig:
    """Build and return master pipeline configuration with env-var overrides.

    Environment variables:
        WHISPER_MODEL: Overrides local Whisper checkpoint (tiny/base/small).
        RSS_FEEDS_JSON: Overrides path to feeds json.
        MIN_HYPE_THRESHOLD: Overrides threshold for high-hype classification.
        ECHO_CHAMBER_EDGE_THRESHOLD: Overrides minimum edge weight in echo-chamber.

    Returns:
        Fully instantiated PipelineConfig instance.
    """
    yaml_cfg = load_yaml_config()

    # Ingestion & whisper
    whisper_model = os.getenv(
        "WHISPER_MODEL",
        yaml_cfg.get("ingestion", {}).get("youtube", {}).get("whisper_model", "small"),
    )

    # Scoring settings
    scoring_data = yaml_cfg.get("hype_scoring", {})
    env_threshold = os.getenv("MIN_HYPE_THRESHOLD")
    min_hype = (
        float(env_threshold)
        if env_threshold
        else float(scoring_data.get("min_hype_threshold", 0.50))
    )

    weights_data = scoring_data.get("weights", {})
    weights = HypeWeights(
        superlative_density=weights_data.get("superlative_density", 0.25),
        subjectivity_score=weights_data.get("subjectivity_score", 0.25),
        clickbait_syntax=weights_data.get("clickbait_syntax", 0.20),
        vague_authority=weights_data.get("vague_authority", 0.15),
        unsubstantiated_claims=weights_data.get("unsubstantiated_claims", 0.15),
    )

    scoring = HypeScoringSettings(
        min_hype_threshold=min_hype,
        weights=weights,
        buzzwords=scoring_data.get("buzzwords", []),
        vague_authorities=scoring_data.get("vague_authorities", []),
    )

    # Echo chamber settings
    echo_data = yaml_cfg.get("echo_chamber", {})
    env_edge_thresh = os.getenv("ECHO_CHAMBER_EDGE_THRESHOLD")
    edge_thresh = (
        float(env_edge_thresh)
        if env_edge_thresh
        else float(echo_data.get("edge_threshold", 0.15))
    )

    echo_chamber = EchoChamberSettings(
        edge_threshold=edge_thresh,
        similarity_metric=echo_data.get("similarity_metric", "hybrid"),
        min_community_size=int(echo_data.get("min_community_size", 2)),
        node_size_metric=echo_data.get("node_size_metric", "hype_score"),
        layout_algorithm=echo_data.get("layout_algorithm", "spring"),
    )

    feeds = load_feeds_config()

    return PipelineConfig(
        whisper_model=whisper_model,
        scoring=scoring,
        echo_chamber=echo_chamber,
        feeds=feeds,
    )
