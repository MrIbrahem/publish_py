r"""The results bundle produced by :class:`.results_loader.ResultsLoader`.

Port of the dict returned by PHP ``Results\GetResults27\ResultsLoader::load()``.
The Python port keeps the bundle data-only (no HTML) — the ``results_2026``
Jinja partials render the cards and tables from this structure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass
class ResultsCounts:
    summary_count: int
    inprocess_count: int
    exists_count: int
    exists_translated_count: int
    exists_translated_before_count: int


@dataclass
class ResultsRows:
    missing_rows: list[dict[str, Any]]
    inprocess_rows: list[dict[str, Any]]
    exists_rows: list[dict[str, Any]]

@dataclass
class ResultsBundle:
    """The results bundle returned by ``results_loader_27()``.

    Consumed by the ``results_2026`` Jinja partials (and enriched with
    ``code_lang_name`` by the route). Mirrors PHP ``Results_tables_2026``.
    """
    counts: ResultsCounts
    rows: ResultsRows
    summary_data: dict[str, Any]
    show_translation_button: str
    tra_type: str
    code_lang_name: str
    full_tr_user: bool


__all__ = [
    "ResultsRows",
    "ResultsCounts",
    "ResultsBundle",
]
