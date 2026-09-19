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

from .....services.utils.wiki_links import get_endpoint
from .bundle import ResultsBundle
from .data import ResultsFetcher
from .helpers import TranslateTypeLoader
from .rows import ExistsRowBuilder, InProcessRowBuilder, MissingRowBuilder

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
        camp: str,
        cat: str,
        tra_type: str,
        code_lang_name: str,
        user_coord: bool,
        settings: dict[str, bool],
        full_tr_user: bool,
        user_is_logged_in: bool,
    ) -> ResultsBundle:
        """
        Build the results bundle for the index page.

        Mirrors PHP ``results_loader_2026($data)`` + ``Results_tables_2026(...)``.
        Returns a :class:`ResultsBundle` with the data the Jinja templates need;
        produces no HTML side effects of its own.
        """
        # logic from results_2026/get_results_2026.php
        bucket = ResultsFetcher().get(cat, code)

        # logic from results_2026/index.php — load_translate_type('no'|'full')
        nolead_titles = TranslateTypeLoader.load("no")
        full_titles = TranslateTypeLoader.load("full")

        # logic from results_2026/index.php — Results_tables_2026
        # Build a lookup of per-title metrics so the inprocess rows can reuse the
        # missing/exists data we already loaded (PHP gets this via
        # get_td_or_sql_titles_infos — a separate large query we deliberately skip).
        titles_infos: dict[str, dict] = {}
        for row in bucket["missing"]:
            titles_infos[row["title"]] = row

        for title, row in bucket["exists"].items():
            titles_infos.setdefault(title, row)

        endpoint = get_endpoint()

        show_btn = settings["show_translation_button"]

        if isinstance(show_btn, str):
            show_btn = show_btn.lower() in ("1", "true", "yes", "on")

        inprocess_button = "1" if (show_btn and user_coord) else "0"

        missing_table = MissingRowBuilder()
        missing_rows = missing_table.build(
            missing=bucket["missing"],
            langcode=code,
            cat=cat,
            camp=camp,
            tra_type=tra_type,
            full_tr_user=full_tr_user,
            nolead_titles=nolead_titles,
            full_titles=full_titles,
            user_is_logged_in=user_is_logged_in,
        )

        inprocess_table = InProcessRowBuilder()
        inprocess_rows = inprocess_table.build(
            inprocess=bucket["inprocess"],
            langcode=code,
            cat=cat,
            camp=camp,
            tra_btn=inprocess_button,
            full_tr_user=full_tr_user,
            titles_infos=titles_infos,
            endpoint=endpoint,
            user_is_logged_in=user_is_logged_in,
        )

        exists_table = ExistsRowBuilder()
        exists_rows, exists_translated_count, exists_translated_before_count = exists_table.build(
            items=bucket["exists"],
            langcode=code,
            cat=cat,
            camp=camp,
            user_coord=user_coord,
            endpoint=endpoint,
            user_is_logged_in=user_is_logged_in,
        )

        return ResultsBundle(
            summary_data=bucket["summary_data"],
            summary_count=len(bucket["missing"]),
            missing_rows=missing_rows,
            inprocess_rows=inprocess_rows,
            inprocess_count=len(bucket["inprocess"]),
            exists_rows=exists_rows,
            exists_count=len(bucket["exists"]),
            exists_translated_count=exists_translated_count,
            exists_translated_before_count=exists_translated_before_count,
            show_translation_button=inprocess_button,
            code=code,
            camp=camp,
            cat=cat,
            tra_type=tra_type or "lead",
            code_lang_name=code_lang_name,
            full_tr_user=full_tr_user,
        )


__all__ = [
    "ResultsLoader",
]
