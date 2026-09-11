"""Feature engineering and Hype / BS metric scoring for text & transcripts.

Extracts multi-dimensional linguistic, syntactic, and structural signals:
- Superlative / exaggeration density
- Sentiment subjectivity
- Clickbait syntax markers (caps ratio, punctuation urgency)
- Vague authority / anonymous citation frequency
- Unsubstantiated claims (qualitative hype vs quantitative grounding)
- Named Entity Recognition (NER count & key entities)
- Composite Hype Score & Categorical Tiers
"""

from __future__ import annotations

import logging
import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
from textblob import TextBlob

from src.config import HypeScoringSettings, get_config

logger = logging.getLogger(__name__)

FINANCIAL_ENTITIES = {
    "NVIDIA", "NVDA", "APPLE", "AAPL", "MICROSOFT", "MSFT", "GOOGLE", "ALPHABET", "GOOGL",
    "TESLA", "TSLA", "AMAZON", "AMZN", "META", "BITCOIN", "BTC", "ETHEREUM", "ETH",
    "SOLANA", "SOL", "FED", "FEDERAL RESERVE", "SEC", "POWELL", "TREASURY", "WALL STREET",
    "GOLDMAN SACHS", "JPMORGAN", "BLACKROCK", "OPENAI", "ANTHROPIC", "TSMC", "AMD",
    "INTEL", "BOEING", "FTC", "DOJ", "S&P 500", "DOW", "NASDAQ", "VIX", "YEN",
    "USDT", "TETHER", "RIPPLE", "XRP", "DEEPMIND", "MISTRAL", "WAYMO"
}


class HypeFeatureExtractor:
    """Computes NLP hype metrics and composite BS scores on text articles."""

    def __init__(self, scoring_cfg: Optional[HypeScoringSettings] = None):
        """Initialize feature extractor with scoring weights and buzzwords.

        Args:
            scoring_cfg: HypeScoringSettings instance. If None, loaded from app config.
        """
        cfg = get_config()
        self.cfg = scoring_cfg or cfg.scoring

        # Compile regex patterns for efficient batch evaluation
        escaped_buzz = [re.escape(w) for w in self.cfg.buzzwords]
        self.buzzword_pattern = (
            re.compile(r"\b(" + "|".join(escaped_buzz) + r")\b", re.IGNORECASE)
            if escaped_buzz
            else None
        )

        escaped_vague = [re.escape(w) for w in self.cfg.vague_authorities]
        self.vague_pattern = (
            re.compile(r"\b(" + "|".join(escaped_vague) + r")\b", re.IGNORECASE)
            if escaped_vague
            else None
        )

        # Regex for quantitative grounding (digits, percentages, currency, dates)
        self.numeric_pattern = re.compile(
            r"(\$\s?\d+(?:,\d+)*(?:\.\d+)?|\b\d+(?:\.\d+)?%|\b\d+(?:,\d+)*(?:\.\d+)?\s?(?:billion|million|trillion|bps|basis points|percent)\b)",
            re.IGNORECASE,
        )

        # Attempt to load spacy if available
        self._spacy_nlp = None
        try:
            import spacy

            try:
                self._spacy_nlp = spacy.load("en_core_web_sm")
            except Exception:
                pass
        except ImportError:
            pass

    def compute_subjectivity(self, text: str) -> float:
        """Calculate sentiment subjectivity in range [0.0, 1.0].

        0.0 = highly objective / wire fact, 1.0 = intensely subjective opinion.

        Args:
            text: Input text string.

        Returns:
            Float subjectivity score.
        """
        if not text or not text.strip():
            return 0.0
        try:
            blob = TextBlob(text)
            return float(round(blob.sentiment.subjectivity, 4))
        except Exception:
            return 0.0

    def compute_superlative_density(self, text: str) -> float:
        """Calculate density of hype buzzwords and extreme intensifiers.

        Args:
            text: Input text string.

        Returns:
            Normalized score in range [0.0, 1.0].
        """
        if not text or not text.strip():
            return 0.0
        words = re.findall(r"\b\w+\b", text)
        total_words = max(len(words), 1)

        matches = (
            len(self.buzzword_pattern.findall(text)) if self.buzzword_pattern else 0
        )
        # 3 or more buzzwords in ~50-100 words yields max density saturation
        ratio = (matches / total_words) * 35.0
        return float(min(1.0, round(ratio, 4)))

    def compute_clickbait_syntax(self, title: str, body: str = "") -> float:
        """Calculate syntactic clickbait signals (caps ratio, punctuation, urgency).

        Args:
            title: Headline or video title.
            body: Optional article body / summary text.

        Returns:
            Normalized score in range [0.0, 1.0].
        """
        if not title:
            return 0.0

        title_clean = title.strip()
        # All-caps word ratio in headline (ignoring 1-letter words)
        words = re.findall(r"\b[A-Za-z]{2,}\b", title_clean)
        caps_words = [w for w in words if w.isupper() and w not in FINANCIAL_ENTITIES]
        caps_ratio = len(caps_words) / max(len(words), 1)

        # Exclamation marks
        excl_count = title_clean.count("!") + (body[:300].count("!") if body else 0)
        excl_score = min(1.0, excl_count * 0.35)

        # Urgency markers & question clickbait
        urgency_regex = re.compile(
            r"\b(urgent|warning|alert|shocking|must watch|before it's too late|don't miss|revealed|hidden truth)\b",
            re.IGNORECASE,
        )
        urgency_match = 1.0 if urgency_regex.search(title_clean) else 0.0
        question_clickbait = 0.5 if title_clean.endswith("?") and (caps_ratio > 0.1 or urgency_match > 0) else 0.0

        score = (0.35 * caps_ratio) + (0.30 * excl_score) + (0.25 * urgency_match) + (0.10 * question_clickbait)
        return float(min(1.0, round(score, 4)))

    def compute_vague_authority(self, text: str) -> float:
        """Calculate score based on anonymous, unverified authority citations.

        Args:
            text: Input text string.

        Returns:
            Normalized score in range [0.0, 1.0].
        """
        if not text or not text.strip():
            return 0.0
        matches = len(self.vague_pattern.findall(text)) if self.vague_pattern else 0
        # 1-2 vague citations saturates the penalty
        score = min(1.0, matches * 0.45)
        return float(round(score, 4))

    def compute_unsubstantiated_claims(self, text: str) -> float:
        """Measure disparity between qualitative assertions and empirical numbers.

        High score indicates high assertions with zero empirical or numeric backing.

        Args:
            text: Input text string.

        Returns:
            Normalized score in range [0.0, 1.0].
        """
        if not text or not text.strip():
            return 0.5
        words = re.findall(r"\b\w+\b", text)
        total_words = max(len(words), 1)

        numeric_matches = len(self.numeric_pattern.findall(text))
        numeric_density = numeric_matches / total_words

        # If text has high word count but zero numbers, penalty is high (0.8+)
        # If text has rich quantitative backing, penalty drops to 0.0
        if numeric_matches == 0:
            return 0.85
        grounding = min(1.0, numeric_density * 40.0)
        return float(round(max(0.0, 1.0 - grounding), 4))

    def extract_named_entities(self, text: str) -> Tuple[int, List[str]]:
        """Extract key named entities and return total count and unique names.

        Uses spaCy if available, with robust regex fallbacks for tickers and orgs.

        Args:
            text: Input text string.

        Returns:
            Tuple of (entity_count, unique_entity_list).
        """
        if not text or not text.strip():
            return 0, []

        entities: Set[str] = set()

        if self._spacy_nlp is not None:
            try:
                doc = self._spacy_nlp(text[:2000])
                for ent in doc.ents:
                    if ent.label_ in ("ORG", "PERSON", "GPE", "PRODUCT", "MONEY"):
                        clean_ent = ent.text.strip().title()
                        if len(clean_ent) > 1:
                            entities.add(clean_ent)
            except Exception:
                pass

        # Regex fallback / enrichment for financial tickers and known institutions
        escaped_fin = [re.escape(e) for e in sorted(FINANCIAL_ENTITIES, key=len, reverse=True)]
        fin_pattern = re.compile(r"\b(" + "|".join(escaped_fin) + r")\b", re.IGNORECASE)
        for match in fin_pattern.findall(text):
            entities.add(match.upper())

        # Clean proper noun phrases
        proper_nouns = re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b", text)
        stop_starters = {"The", "This", "That", "With", "After", "Before", "Over", "Into", "Why", "How"}
        for pn in proper_nouns[:6]:
            parts = pn.split()
            if parts[0] not in stop_starters and len(pn) > 4:
                entities.add(pn.title())

        entity_list = sorted(list(entities))
        return len(entity_list), entity_list

    def calculate_hype_score(
        self,
        superlative: float,
        subjectivity: float,
        clickbait: float,
        vague_auth: float,
        unsubstantiated: float,
        outlet_weight: float = 1.0,
    ) -> float:
        """Compute composite weighted hype score.

        Args:
            superlative: Superlative density score [0, 1].
            subjectivity: Sentiment subjectivity score [0, 1].
            clickbait: Clickbait syntax score [0, 1].
            vague_auth: Vague authority citation score [0, 1].
            unsubstantiated: Disparity metric score [0, 1].
            outlet_weight: Optional prior multiplier based on outlet history.

        Returns:
            Final composite hype score clamped in [0.0, 1.0].
        """
        w = self.cfg.weights
        raw_score = (
            w.superlative_density * superlative
            + w.subjectivity_score * subjectivity
            + w.clickbait_syntax * clickbait
            + w.vague_authority * vague_auth
            + w.unsubstantiated_claims * unsubstantiated
        )
        # Apply outlet weight moderately
        weighted_score = raw_score * (0.8 + 0.2 * outlet_weight)
        return float(min(1.0, max(0.0, round(weighted_score, 4))))

    @staticmethod
    def get_hype_tier(score: float) -> str:
        """Convert continuous score into qualitative tier label.

        Args:
            score: Numeric hype score [0, 1].

        Returns:
            Qualitative tier description string.
        """
        if score < 0.25:
            return "Low Hype (Objective / Wire)"
        elif score < 0.50:
            return "Moderate Buzz"
        elif score < 0.75:
            return "High Hype / Sensational"
        else:
            return "Critical BS / Speculative Frenzy"

    def analyze_item(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Perform full feature extraction for a single media item.

        Args:
            row: Dictionary with keys 'title', 'summary', 'outlet_weight', etc.

        Returns:
            Dictionary enriched with all computed NLP metrics.
        """
        title = str(row.get("title", ""))
        summary = str(row.get("summary", "") or row.get("full_text", ""))
        combined_text = f"{title}. {summary}"
        outlet_weight = float(row.get("outlet_weight", 1.0))

        subj = self.compute_subjectivity(combined_text)
        sup = self.compute_superlative_density(combined_text)
        clickbait = self.compute_clickbait_syntax(title, summary)
        vague = self.compute_vague_authority(combined_text)
        unsub = self.compute_unsubstantiated_claims(combined_text)
        ner_count, entities = self.extract_named_entities(combined_text)

        hype_score = self.calculate_hype_score(
            superlative=sup,
            subjectivity=subj,
            clickbait=clickbait,
            vague_auth=vague,
            unsubstantiated=unsub,
            outlet_weight=outlet_weight,
        )

        tier = self.get_hype_tier(hype_score)
        is_flagged = hype_score >= self.cfg.min_hype_threshold

        return {
            **row,
            "subjectivity_score": subj,
            "superlative_density": sup,
            "clickbait_syntax": clickbait,
            "vague_authority_score": vague,
            "unsubstantiated_score": unsub,
            "ner_count": ner_count,
            "entities": entities,
            "hype_score": hype_score,
            "hype_tier": tier,
            "is_flagged": is_flagged,
        }

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features and scores across an entire DataFrame.

        Args:
            df: Input DataFrame containing raw articles.

        Returns:
            Enriched pandas DataFrame with feature columns.
        """
        if df.empty:
            return pd.DataFrame()

        records = df.to_dict(orient="records")
        analyzed_records = [self.analyze_item(rec) for rec in records]
        return pd.DataFrame(analyzed_records)
