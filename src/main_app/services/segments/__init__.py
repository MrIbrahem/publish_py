"""
Library package for CX server.

from html_to_segments import process_html

process_html(
    source_html: str,
    lang: str | None = None,
    sort_attrs: bool = True,
    wrap_sections: bool = True,
) -> Doc:

"""

from __future__ import annotations

from .lib.mw.mw_page_loader import MWPageLoader
from .lib.processor import process_html

run_process_html = process_html

__all__ = [
    "MWPageLoader",
    "process_html",
    "run_process_html",
]
