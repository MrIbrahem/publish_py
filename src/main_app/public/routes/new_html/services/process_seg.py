""" """

from __future__ import annotations

import logging
from pathlib import Path

from ...html_to_segments import process_html
from .html_utils import remove_data_parsoid
from .storage import read_file

logger = logging.getLogger(__name__)


def get_segments(source_html: str, file_seg: Path, force_new: bool) -> tuple[str, bool]:
    """ """
    from_cache = False

    # check cache
    if not force_new:
        cached = read_file(file_seg)
        if cached:
            cached = remove_data_parsoid(cached)  # not in php
            return cached, True

    # check if html_text is empty
    if not source_html:
        return "", from_cache

    try:
        seg_text = process_html(source_html)  # Process the HTML content
    except Exception as e:
        logger.error("Segment processing failed: %s", e)
        return "", from_cache

    if not seg_text:
        return "", from_cache

    # Normalize known empty messages (if any)
    if seg_text in (
        "Content for translate is not given or is empty",
        "Sectionwrap: Attempting to remove a non-section tag: undefined",
    ):
        return "", from_cache

    # php write to file before remove_data_parsoid
    seg_text = remove_data_parsoid(seg_text)

    return seg_text, from_cache


__all__ = [
    "get_segments",
]
