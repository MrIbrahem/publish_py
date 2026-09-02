"""
HTML post-processing utilities.

Currently only implements remove_data_parsoid.

TODO: Port the remaining helpers from the original PHP HtmlUtils:
      - del_div_error
      - fix_link_red
"""

from __future__ import annotations

import re


def remove_data_parsoid(html: str) -> str:
    """
    Remove data-parsoid attributes from HTML.

    This mirrors the behavior of the original PHP function.
    """
    if not html:
        return ""

    # Remove empty data-parsoid="{}"
    html = re.sub(r'\s*data-parsoid\s*=\s*"{}"', "", html, flags=re.IGNORECASE)

    # Remove data-parsoid='...'
    html = re.sub(r"\s*data-parsoid\s*=\s*'[^']*'", "", html, flags=re.IGNORECASE)

    # Remove data-parsoid="..."
    html = re.sub(r'\s*data-parsoid\s*=\s*"[^"]*"', "", html, flags=re.IGNORECASE)

    return html


__all__ = [
    "remove_data_parsoid",
]
