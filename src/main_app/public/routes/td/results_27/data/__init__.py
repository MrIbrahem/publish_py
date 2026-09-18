"""
Data layer for the results_27 module (port of ``results_27/Data``).
"""

from __future__ import annotations

from .results_fetcher import ResultsFetcher, get_results_27

__all__ = [
    "ResultsFetcher",
    "get_results_27",
]
