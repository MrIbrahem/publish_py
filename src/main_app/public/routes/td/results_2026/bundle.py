"""
The results bundle produced by :class:`.results_loader.ResultsLoader`.

Port of the dict returned by PHP ``ResultsLoader::load()``.
The Python port keeps the bundle data-only (no HTML) — the ``results_2026``
Jinja partials render the cards and tables from this structure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .mapping import ExistsItem, InProcessItem, MissingItem


@dataclass
class ResultsCounts:
    summary_count: int
    inprocess_count: int
    exists_count: int
    exists_translated_count: int
    exists_translated_before_count: int


@dataclass
class ResultsRows:
    missing_rows: list[MissingItem]
    inprocess_rows: list[InProcessItem]
    exists_rows: list[ExistsItem]

    def to_json(self) -> dict[str, Any]:
        return {
            "missing": [x.to_json() for x in self.missing_rows],
            "inprocess": [x.to_json() for x in self.inprocess_rows],
            "exists": [x.to_json() for x in self.exists_rows],
        }


@dataclass
class ResultsBundle:
    """The results bundle returned by ``results_loader_27()``.

    Consumed by the ``results_2026`` Jinja partials (and enriched with
    ``code_lang_name`` by the route). Mirrors PHP ``Results_tables_2026``.
    """

    counts: ResultsCounts
    rows: ResultsRows
    summary_data: dict[str, Any]
    show_translation_button: bool
    tr_type: str
    code_lang_name: str
    full_tr_user: bool

    def to_api_json(self) -> dict[str, dict[str, Any]]:
        return {
            "rows": self.rows.to_json(),
            "summary_data": self.summary_data,
        }


__all__ = [
    "ResultsRows",
    "ResultsCounts",
    "ResultsBundle",
]
