"""Unit tests for data ingestion in src/ingest.py."""

from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from src.config import FeedConfig
from src.ingest import RSSIngester, YouTubeIngester, clean_html


def test_clean_html() -> None:
    """Test HTML stripping and whitespace collapsing."""
    raw = "<p>This is a <b>bold</b> claim with &amp; symbols.<br></p>"
    cleaned = clean_html(raw)
    assert cleaned == "This is a bold claim with & symbols."
    assert clean_html("") == ""


def test_rss_sample_loading() -> None:
    """Test loading the pre-cached RSS sample fixture."""
    df = RSSIngester.load_cached_sample()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 100
    assert "title" in df.columns
    assert "outlet" in df.columns
    assert "summary" in df.columns
    assert df["outlet"].nunique() >= 8


def test_youtube_transcript_loading() -> None:
    """Test loading the sample YouTube influencer audio transcript fixture."""
    data = YouTubeIngester.load_cached_transcript()
    assert isinstance(data, dict)
    assert "title" in data
    assert "full_transcript" in data
    assert "segments" in data
    assert len(data["segments"]) > 0


def test_feedparser_mock_parsing() -> None:
    """Test RSSIngester.fetch_live_feed with mocked feedparser response."""
    ingester = RSSIngester(feeds=[])

    mock_entry = MagicMock()
    mock_entry.title = "Mock Headline on Wall Street"
    mock_entry.summary = "<p>Mock summary text with detailed reporting.</p>"
    mock_entry.link = "https://example.com/mock-article"
    mock_entry.published = "2026-09-11T10:00:00Z"
    mock_entry.author = "Mock Reporter"

    mock_parsed = MagicMock()
    mock_parsed.entries = [mock_entry]

    feed_cfg = FeedConfig(
        id="mock_feed",
        name="Mock Financial Gazette",
        category="Finance",
        url="https://example.com/feed.xml",
        bias_label="Neutral",
        weight=1.0,
    )

    with patch("feedparser.parse", return_value=mock_parsed):
        articles = ingester.fetch_live_feed(feed_cfg, max_items=5)

    assert len(articles) == 1
    item = articles[0]
    assert item["outlet"] == "Mock Financial Gazette"
    assert item["title"] == "Mock Headline on Wall Street"
    assert item["summary"] == "Mock summary text with detailed reporting."
    assert item["link"] == "https://example.com/mock-article"
