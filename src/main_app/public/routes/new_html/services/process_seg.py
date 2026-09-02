"""
"""

from __future__ import annotations

import logging
from pathlib import Path

from ...html_to_segments import process_html
from .html_utils import remove_data_parsoid
from .storage import (
    read_file,
    write_file,
)

logger = logging.getLogger(__name__)

def get_segments(html: str, file_seg: Path, force_new: bool) -> tuple[str, bool]:
    """

    """
    from_cache = False

    if not force_new:
        cached = read_file(file_seg)
        if cached:
            cached = remove_data_parsoid(cached) # not in php
            return cached, True

    if not html:
        return "", from_cache

    try:
        seg = process_html(html)
    except Exception as e:
        logger.error("Segment processing failed: %s", e)
        return "", from_cache

    if not seg:
        return "", from_cache

    # Normalize known empty messages (if any)
    if seg in (
        "Content for translate is not given or is empty",
        "Sectionwrap: Attempting to remove a non-section tag: undefined",
    ):
        return "", from_cache

    seg = remove_data_parsoid(seg)
    write_file(file_seg, seg)

    return seg, from_cache


__all__ = [
    "get_segments",
]
