""" """

from __future__ import annotations

import logging
from pathlib import Path

from ..clients import TransformApiService
from ..utils import FileUtils

logger = logging.getLogger(__name__)


class WikitextToHtmlService:
    """HTML conversion services.

    Provides functions for converting wikitext to HTML using the
    Wikipedia REST API, with caching support.
    """

    def __init__(
        self,
        transform_service: TransformApiService | None = None,
    ) -> None:
        """Initialize the service."""
        self.transform_service = transform_service or TransformApiService()

    def convert(
        self,
        wikitext: str,
        title: str,
    ) -> str:
        """Convert wikitext to HTML."""

        # fast return if wikitext is empty
        if not wikitext:
            return ""

        title = title.replace(" ", "_")

        fixed = self.transform_service.convert(wikitext, title)

        # Handle both dictionary and object responses gracefully
        if isinstance(fixed, dict):
            result = fixed.get("result", "")
        else:
            result = getattr(fixed, "result", "")

        # HTML conversion failed
        if not result or result == wikitext:
            logger.error("HTML conversion failed for title: %s", title)
            return ""
        return result

    def convert_with_cache(
        self,
        wikitext: str,
        file_html: str | Path,
        title: str,
        force_new: bool,
    ) -> tuple[str, bool]:
        """Convert wikitext to HTML with caching support."""
        file_path = Path(file_html)
        # 1. check from cache
        if not force_new:
            cached = FileUtils.read_file(file_path)
            if cached:
                return cached, True

        # fast return if wikitext is empty
        if not wikitext:
            return "", False

        html = self.convert(wikitext, title)

        # HTML conversion failed
        if not html:
            logger.error("HTML conversion failed for title: %s", title)
            return "", False

        # remove data parsoid and save file
        FileUtils.write_file(file_path, html)

        return html, False


__all__ = [
    "WikitextToHtmlService",
]
