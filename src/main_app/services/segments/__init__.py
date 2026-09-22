"""
Library package for CX server.
"""

from __future__ import annotations

from .lib.processor import process_html

run_process_html = process_html

__all__ = [
    "process_html",
    "run_process_html",
]
