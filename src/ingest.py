"""Multi-modal ingestion pipeline for BS & Hype Analyzer.

Provides robust ingestors for:
1. Live and cached RSS news/finance feeds (Bloomberg, Reuters, CNBC, etc.)
2. YouTube financial influencer audio extraction and local Whisper transcription.
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from bs4 import BeautifulSoup

from src.config import (
    CONFIG_DIR,
    INTERIM_DATA_DIR,
    RAW_DATA_DIR,
    FeedConfig,
    get_config,
    load_feeds_config,
)

logger = logging.getLogger(__name__)


def clean_html(raw_html: str) -> str:
    """Strip HTML markup and collapse whitespace.

    Args:
        raw_html: Raw HTML or formatted text string.

    Returns:
        Clean plain text string.
    """
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


class RSSIngester:
    """Ingests articles from configured RSS feeds."""

    def __init__(self, feeds: Optional[List[FeedConfig]] = None):
        """Initialize RSS ingester.

        Args:
            feeds: List of FeedConfig instances. If None, loads from config.
        """
        self.feeds = feeds or load_feeds_config()

    def fetch_live_feed(
        self, feed_cfg: FeedConfig, max_items: int = 20
    ) -> List[Dict[str, Any]]:
        """Fetch and parse a single RSS feed live over HTTP.

        Args:
            feed_cfg: Target feed configuration.
            max_items: Maximum articles to fetch.

        Returns:
            List of parsed article dictionaries.
        """
        try:
            import feedparser  # lazy import
        except ImportError:
            logger.warning("feedparser not installed; falling back to empty feed.")
            return []

        logger.info("Fetching RSS from %s (%s)", feed_cfg.name, feed_cfg.url)
        parsed = feedparser.parse(feed_cfg.url)
        articles: List[Dict[str, Any]] = []

        for entry in parsed.entries[:max_items]:
            raw_summary = getattr(entry, "summary", "") or getattr(
                entry, "description", ""
            )
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "")
            published = getattr(entry, "published", "") or datetime.now(
                timezone.utc
            ).isoformat()
            author = getattr(entry, "author", "Editorial Staff")

            articles.append(
                {
                    "id": f"{feed_cfg.id}_{abs(hash(link or title)) % 1000000:06d}",
                    "outlet": feed_cfg.name,
                    "outlet_id": feed_cfg.id,
                    "category": feed_cfg.category,
                    "bias_label": feed_cfg.bias_label,
                    "source_type": "rss",
                    "title": clean_html(title),
                    "summary": clean_html(raw_summary),
                    "link": link,
                    "published": published,
                    "author": author,
                    "outlet_weight": feed_cfg.weight,
                }
            )
        return articles

    def fetch_all(self, max_items_per_feed: int = 20) -> pd.DataFrame:
        """Fetch all configured RSS feeds.

        Args:
            max_items_per_feed: Max articles per outlet.

        Returns:
            pandas DataFrame containing all collected articles.
        """
        all_articles: List[Dict[str, Any]] = []
        for feed in self.feeds:
            try:
                items = self.fetch_live_feed(feed, max_items=max_items_per_feed)
                all_articles.extend(items)
            except Exception as e:
                logger.error("Failed to fetch feed %s: %s", feed.name, e)

        df = pd.DataFrame(all_articles)
        if not df.empty:
            df.drop_duplicates(subset=["title"], inplace=True)
        return df

    @staticmethod
    def load_cached_sample(
        sample_path: Optional[Path] = None,
    ) -> pd.DataFrame:
        """Load pre-cached sample RSS dataset for offline evaluation.

        Args:
            sample_path: Path to sample JSON file. Defaults to data/raw/sample_rss_feeds.json.

        Returns:
            pandas DataFrame with parsed sample articles.
        """
        path = sample_path or (RAW_DATA_DIR / "sample_rss_feeds.json")
        if not path.exists():
            raise FileNotFoundError(f"Sample RSS feed not found at {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        articles = data.get("articles", [])
        df = pd.DataFrame(articles)
        if "source_type" not in df.columns:
            df["source_type"] = "rss"
        return df


class YouTubeIngester:
    """Extracts audio and generates transcriptions locally using Whisper."""

    def __init__(self, whisper_model: Optional[str] = None, device: str = "auto"):
        """Initialize YouTube/Audio ingester.

        Args:
            whisper_model: Model name ('tiny', 'base', 'small', 'medium').
            device: 'cuda', 'cpu', or 'auto'.
        """
        cfg = get_config()
        self.whisper_model_name = whisper_model or cfg.whisper_model
        self.device = device
        self._model = None

    def _get_whisper_model(self) -> Any:
        """Lazy loader for whisper model."""
        if self._model is None:
            try:
                import whisper

                logger.info("Loading local Whisper model: %s", self.whisper_model_name)
                self._model = whisper.load_model(self.whisper_model_name)
            except ImportError:
                logger.warning("openai-whisper is not installed.")
                return None
        return self._model

    def transcribe_audio_file(self, audio_path: Path) -> Dict[str, Any]:
        """Transcribe a local audio file using Whisper.

        Args:
            audio_path: Path to audio file.

        Returns:
            Dictionary with transcription text, language, and segments.
        """
        model = self._get_whisper_model()
        if model is None:
            return {
                "text": "[Transcription unavailable: whisper not installed]",
                "language": "en",
                "segments": [],
            }
        result = model.transcribe(str(audio_path))
        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", "en"),
            "segments": result.get("segments", []),
        }

    def download_audio_from_youtube(
        self, video_url: str, output_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """Download audio track from a YouTube video via yt-dlp.

        Args:
            video_url: Target YouTube video URL.
            output_dir: Directory to save downloaded audio.

        Returns:
            Path to downloaded audio file, or None if failed.
        """
        out_dir = output_dir or INTERIM_DATA_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            import yt_dlp

            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "wav",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
                "quiet": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                video_id = info.get("id")
                return out_dir / f"{video_id}.wav"
        except Exception as e:
            logger.error("Failed to download audio from YouTube: %s", e)
            return None

    @staticmethod
    def load_cached_transcript(
        sample_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Load pre-cached YouTube transcript sample.

        Args:
            sample_path: Path to sample transcript JSON.

        Returns:
            Parsed transcript dictionary.
        """
        path = sample_path or (RAW_DATA_DIR / "sample_youtube_transcript.json")
        if not path.exists():
            raise FileNotFoundError(f"Cached transcript not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def ingest_all(use_sample: bool = True) -> pd.DataFrame:
    """Run end-to-end ingestion across all modalities (RSS + Video transcripts).

    Args:
        use_sample: If True, uses cached local samples for instant reproduction.

    Returns:
        Consolidated pandas DataFrame of media items.
    """
    if use_sample:
        logger.info("Loading cached RSS sample dataset...")
        df_rss = RSSIngester.load_cached_sample()
        try:
            yt_data = YouTubeIngester.load_cached_transcript()
            # Append video sample as a media article row
            video_row = {
                "id": yt_data.get("video_id", "yt_sample_001"),
                "outlet": yt_data.get("channel", "YouTube Finance Influencer"),
                "outlet_id": "yt_influencer",
                "category": "Social Media / Video",
                "bias_label": "High-Speculation Social Influencer",
                "source_type": "audio_transcript",
                "title": yt_data.get("title", "Crypto & Stock Hype Video"),
                "summary": yt_data.get("full_transcript", "")[:500] + "...",
                "link": yt_data.get("url", "https://youtube.com/watch?v=sample"),
                "published": yt_data.get(
                    "published_at", datetime.now(timezone.utc).isoformat()
                ),
                "author": yt_data.get("speaker", "Crypto Alpha Moonshots"),
                "outlet_weight": 1.5,
                "full_text": yt_data.get("full_transcript", ""),
            }
            df_rss = pd.concat([df_rss, pd.DataFrame([video_row])], ignore_index=True)
        except Exception as e:
            logger.warning("Could not append YouTube sample: %s", e)
        return df_rss
    else:
        logger.info("Fetching live feeds from RSS sources...")
        ingester = RSSIngester()
        df = ingester.fetch_all()
        return df
