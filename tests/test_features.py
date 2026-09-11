"""Unit tests for NLP feature extraction and hype scoring in src/features.py."""

import pandas as pd
import pytest

from src.features import HypeFeatureExtractor


@pytest.fixture
def extractor() -> HypeFeatureExtractor:
    """Fixture to provide a configured HypeFeatureExtractor."""
    return HypeFeatureExtractor()


def test_subjectivity_computation(extractor: HypeFeatureExtractor) -> None:
    """Test sentiment subjectivity scoring on objective vs highly subjective statements."""
    objective_text = (
        "The government reported nonfarm payroll growth of 175,000 jobs last month."
    )
    subjective_text = (
        "This is the most incredible, terrifying, and disastrous investment mistake ever!"
    )

    subj_obj = extractor.compute_subjectivity(objective_text)
    subj_sub = extractor.compute_subjectivity(subjective_text)

    assert 0.0 <= subj_obj <= 0.20, f"Objective text scored too high: {subj_obj}"
    assert subj_sub >= 0.50, f"Subjective text scored too low: {subj_sub}"
    assert extractor.compute_subjectivity("") == 0.0


def test_superlative_density(extractor: HypeFeatureExtractor) -> None:
    """Test that buzzwords and extreme intensifiers trigger higher density scores."""
    grounded_text = "Nvidia shipped 100,000 graphics processors to enterprise clients."
    hyped_text = (
        "This revolutionary game-changer will skyrocket 100x to the moon before an unprecedented bloodbath!"
    )

    score_low = extractor.compute_superlative_density(grounded_text)
    score_high = extractor.compute_superlative_density(hyped_text)

    assert score_low == 0.0
    assert score_high >= 0.50
    assert 0.0 <= score_high <= 1.0


def test_clickbait_syntax(extractor: HypeFeatureExtractor) -> None:
    """Test all-caps ratios, exclamation markers, and urgency clickbait syntax."""
    neutral_title = "Treasury Yields Stabilize Following Inflation Report"
    clickbait_title = "URGENT WARNING: WHY YOU MUST SELL YOUR STOCKS RIGHT NOW!!!"

    score_neutral = extractor.compute_clickbait_syntax(neutral_title)
    score_clickbait = extractor.compute_clickbait_syntax(clickbait_title)

    assert score_neutral <= 0.20
    assert score_clickbait >= 0.60


def test_vague_authority(extractor: HypeFeatureExtractor) -> None:
    """Test detection of unverified anonymous claims ('sources say', 'experts warn')."""
    sourced_text = "According to Department of Commerce official records released today."
    vague_text = "Insiders suggest and top experts warn that market whispers point to a crash."

    score_clean = extractor.compute_vague_authority(sourced_text)
    score_vague = extractor.compute_vague_authority(vague_text)

    assert score_clean == 0.0
    assert score_vague >= 0.40


def test_unsubstantiated_claims(extractor: HypeFeatureExtractor) -> None:
    """Test quantitative grounding penalty when claims lack numeric/empirical data."""
    grounded_text = "Revenue grew 24.5% to $4.2 billion with EPS rising 12% to $1.15 per share."
    ungrounded_text = "The company is experiencing immense, boundless expansion across every single vertical."

    score_grounded = extractor.compute_unsubstantiated_claims(grounded_text)
    score_ungrounded = extractor.compute_unsubstantiated_claims(ungrounded_text)

    assert score_grounded <= 0.40
    assert score_ungrounded >= 0.70


def test_named_entities_and_ner_count(extractor: HypeFeatureExtractor) -> None:
    """Test extraction of recognized entities and accurate count."""
    text = "Nvidia, Apple, and the Federal Reserve are closely monitored by Wall Street and Jerome Powell."
    count, entities = extractor.extract_named_entities(text)

    assert count >= 3
    assert "NVIDIA" in entities
    assert "APPLE" in entities
    assert any("FEDERAL RESERVE" in e or "POWELL" in e or "WALL STREET" in e for e in entities)


def test_calculate_hype_score_and_tiers(extractor: HypeFeatureExtractor) -> None:
    """Test composite hype score bounds, weighting, and tier labeling."""
    low_score = extractor.calculate_hype_score(
        superlative=0.0,
        subjectivity=0.1,
        clickbait=0.0,
        vague_auth=0.0,
        unsubstantiated=0.2,
    )
    high_score = extractor.calculate_hype_score(
        superlative=0.9,
        subjectivity=0.8,
        clickbait=0.9,
        vague_auth=0.8,
        unsubstantiated=0.9,
    )

    assert 0.0 <= low_score < 0.25
    assert high_score >= 0.70

    assert "Low Hype" in extractor.get_hype_tier(0.15)
    assert "Moderate Buzz" in extractor.get_hype_tier(0.40)
    assert "High Hype" in extractor.get_hype_tier(0.65)
    assert "Critical BS" in extractor.get_hype_tier(0.85)


def test_process_dataframe(extractor: HypeFeatureExtractor) -> None:
    """Test batch processing of a DataFrame containing multiple articles."""
    df_raw = pd.DataFrame(
        [
            {
                "id": "test_01",
                "outlet": "Wire News",
                "title": "Fed Holds Rates at 5.25%",
                "summary": "The central bank maintained benchmark rates today.",
                "outlet_weight": 1.0,
            },
            {
                "id": "test_02",
                "outlet": "Speculative Blog",
                "title": "URGENT: 100x Moonshot Opportunity Guaranteed!",
                "summary": "Insiders reveal this revolutionary token will explode overnight!",
                "outlet_weight": 1.4,
            },
        ]
    )

    df_res = extractor.process_dataframe(df_raw)
    assert len(df_res) == 2
    assert "hype_score" in df_res.columns
    assert "is_flagged" in df_res.columns
    assert df_res.iloc[1]["hype_score"] > df_res.iloc[0]["hype_score"]
