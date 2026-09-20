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
from typing import Any

from .bundle import ResultsBundle, ResultsCounts, ResultsRows
from .data import ResultsFetcher
from .helpers import TranslateTypeLoader
from .tables import ExistsTable, InProcessTable, MissingTable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


class ResultsLoader:
    """Builds the results bundle for the index page."""

    def load(
        self,
        *,
        code: str,
        cat: str,
        tra_type: str,
        code_lang_name: str,
        settings: dict[str, bool],
        full_tr_user: bool,
    ) -> ResultsBundle:
        """
        Build the results bundle for the index page.

        Returns a :class:`ResultsBundle` with the data the Jinja templates need;
        produces no HTML side effects of its own.
        """
        # logic from results_2026/get_results_2026.php
        bucket = ResultsFetcher().get(cat, code)

        # logic from results_2026/index.php — load_translate_type('no'|'full')
        translation_loader = TranslateTypeLoader()
        translation_loader._load()
        rows_data = translation_loader.rows_data

        def to_bool(val: Any) -> bool:
            if isinstance(val, str):
                return val.lower() in ("1", "true", "yes", "on")
            return bool(val)

        show_btn = to_bool(settings["show_translation_button"])

        # Under testing
        # show_translation_button = show_btn and user_coord

        missing_table = MissingTable(
            tra_type=tra_type,
            full_tr_user=full_tr_user,
            translate_type_data=rows_data,
        )
        missing_rows = missing_table.build(bucket["missing"])

        inprocess_table = InProcessTable(translate_type_data=rows_data)
        inprocess_rows = inprocess_table.build(bucket["inprocess"])

        exists_table = ExistsTable(translate_type_data=rows_data)

        exists_rows = exists_table.build(bucket["exists"])
        exists_translated_count, exists_translated_before_count = exists_table.count_status(exists_rows)

        return ResultsBundle(
            rows=ResultsRows(
                missing_rows=missing_rows,
                inprocess_rows=inprocess_rows,
                exists_rows=exists_rows,
            ),
            counts=ResultsCounts(
                summary_count=len(bucket["missing"]),
                inprocess_count=len(bucket["inprocess"]),
                exists_count=len(bucket["exists"]),
                exists_translated_count=exists_translated_count,
                exists_translated_before_count=exists_translated_before_count,
            ),
            summary_data=bucket["summary_data"],
            show_translation_button=show_btn,
            tra_type=tra_type or "lead",
            code_lang_name=code_lang_name,
            full_tr_user=full_tr_user,
        )


__all__ = [
    "ResultsLoader",
]
