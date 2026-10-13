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
    def get_segments(self, source_html: str, file_seg: Path, force_new: bool) -> tuple[str, bool]:
        """
        return segments text and from_cache
        """
        # check cache
        if not force_new:
            cached = FileUtils.read_file(file_seg)
            if cached:
                return cached, True

        # check if html_text is empty
        if not source_html:
            return "", False

        try:
            seg_text = run_process_html(source_html)  # Process the HTML content
        except Exception as e:
            logger.error("Segment processing failed: %s", e)
            return "", False

        if not seg_text:
            return "", False

        # Normalize known empty messages (if any)
        if seg_text in (
            "Content for translate is not given or is empty",
            "Sectionwrap: Attempting to remove a non-section tag: undefined",
        ):
            return "", False

        return seg_text, False


__all__ = [
    "HtmlToSegmentsService",
]
