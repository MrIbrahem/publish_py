"""
Row items for the results_2026 module.

Each item is a small dataclass holding one row's own data; the Jinja partials
call ``render(...)`` with the request-level context (langcode/camp/auth flags)
to emit the ``<tr>`` markup — see ``templates/td/results_2026/*.html``.
"""

from __future__ import annotations

from .mapping import ExistsItem, InProcessItem, MissingItem

__all__ = [
    "MissingItem",
    "ExistsItem",
    "InProcessItem",
]
