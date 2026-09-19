"""
Row items for the results_2026 module.

Each item is a small dataclass holding one row's own data; the Jinja partials
call ``render(...)`` with the request-level context (langcode/camp/auth flags)
to emit the ``<tr>`` markup — see ``templates/td/results_2026/*.html``.
"""

from __future__ import annotations

from .exists_row_builder import ExistsRowBuilder
from .in_process_row_builder import InProcessRowBuilder
from .missing_row_builder import MissingRowBuilder

__all__ = [
    "MissingRowBuilder",
    "ExistsRowBuilder",
    "InProcessRowBuilder",
]
