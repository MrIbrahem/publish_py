""" """

from __future__ import annotations

import logging
from pathlib import Path

from ....services.segments_wraper import run_process_html
from ..utils import FileUtils

logger = logging.getLogger(__name__)


class HtmlToSegmentsService:
    """HTML segmentation services.

    Provides functions for converting HTML to segmented content using
    the HtmltoSegments API, with caching support.
    """

    REPLACE_URLS = {
        "https://medwiki.toolforge.org/md/": "https://en.wikipedia.org/w/",
        "https://medwiki.toolforge.org/w/": "https://en.wikipedia.org/w/",
        "https://medwiki.toolforge.org/wiki/": "https://en.wikipedia.org/wiki/",
    }

    # Messages returned by the segmentation service that mean "no content"
    SEG_EMPTY_MESSAGES = [
        "Content for translate is not given or is empty",
        "Sectionwrap: Attempting to remove a non-section tag: undefined",
    ]

    def get_segments(self, source_html: str, file_path: Path, force_new: bool = False) -> tuple[str, bool]:
        """
        Convert HTML to segments with caching support.

        :param text: The HTML text to convert
        :param file_path: The path to the cached segments file
        :param force_new: Whether to force regeneration (True) or use cache (False)
        :return: Tuple containing [segments, from_cache]
        """
        # check cache
        if not force_new:
            cached = FileUtils.read_file(file_path)
            if cached:
                return cached, True

        # check if html_text is empty
        if not source_html:
            return "", False

        result = self._request_new_content(source_html)

        return result, False

    def _request_new_content(self, text: str) -> str:
        """Convert HTML to segments using the API.

        :param text: The HTML text to convert
        :return: The segmented result or empty string on failure
        """
        try:
            seg_text = run_process_html(text)  # Process the HTML content
        except Exception as e:
            logger.error("Segment processing failed: %s", e)
            return ""

        if not seg_text:
            return ""

        # Normalize known empty messages (if any)
        return self._modify_text_segments(seg_text)

    @staticmethod
    def _modify_text_segments(text: str) -> str:
        """Modify text segments by replacing URLs and handling empty messages."""
        for from_url, to_url in HtmlToSegmentsService.REPLACE_URLS.items():
            text = text.replace(from_url, to_url)

        if text in HtmlToSegmentsService.SEG_EMPTY_MESSAGES:
            text = ""

        return text


__all__ = [
    "HtmlToSegmentsService",
]
