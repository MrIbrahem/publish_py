"""
Python port of the PHP ``Results\\GetResults2026`` module.

Reference PHP files:
  - src/backend/results_2026/index.php           (results_loader_2026, Results_tables_2026, load_translate_type)
  - src/backend/results_2026/get_results_2026.php (get_results_2026, getinprocess_n)
  - src/backend/results_2026/results_table.php   (_make_one_row_results, make_results_table_2026)
  - src/backend/results_2026/results_table_exists.php (make_one_row_exists_2026, make_results_table_exists_2026)
  - src/backend/results_2026/results_table_inprocess.php (make_one_row_new_inprocess, make_results_table_inprocess)
  - src/results/helps.php                        (make_translate_urls)

The orchestrator returns a :class:`ResultsBundle` (the "results bundle") that
``templates/index.html`` consumes via three Jinja partials.
"""

from __future__ import annotations

import logging

from .....database.services import (
    InProcessService,
)

logger = logging.getLogger(__name__)


def get_inprocess_for_missing(missing_titles: set[str], code: str) -> dict[str, dict]:
    """Mirror of PHP ``getinprocess_n($missing, $code)``."""
    service = InProcessService()
    records = service.list_in_process_by_lang(code)
    result: dict[str, dict] = {}
    for r in records:
        if r.title not in missing_titles:
            continue
        result[r.title] = {
            "id": r.id,
            "title": r.title,
            "user": r.user or "",
            "lang": r.lang,
            "cat": r.cat or "",
            "translate_type": r.translate_type or "",
            "word": r.word or 0,
            "add_date": r.add_date,  # datetime or None
        }
    return result


__all__ = [
    "get_inprocess_for_missing",
]
