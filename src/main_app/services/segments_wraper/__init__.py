"""
Library package for CX server.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from html_to_segments import process_html

    _process_html = process_html
except ImportError:
    _process_html = None


def run_process_html(*args, **kwargs):
    if _process_html is None:
        logger.error("html_to_segments library is not installed")
        return None

    return _process_html(*args, **kwargs)


__all__ = [
    "run_process_html",
]
