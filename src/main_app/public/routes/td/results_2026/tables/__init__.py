"""
Tables for the results_27 module (port of ``results_27/Tables``).
"""

from __future__ import annotations

from .exists_table import ExistsTable
from .in_process_table import InProcessTable
from .missing_table import MissingTable

__all__ = [
    "MissingTable",
    "ExistsTable",
    "InProcessTable",
]
