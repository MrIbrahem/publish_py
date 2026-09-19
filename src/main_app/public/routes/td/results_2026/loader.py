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

from .....database.services import PagesService
from .....database.services.pages import Results2026Service
from .....services.utils.wiki_links import get_endpoint
from .bundle import ResultsBundle
from .results import (
    build_exists_rows,
    build_inprocess_rows,
    build_missing_rows,
    get_inprocess_for_missing,
    load_translate_type_sets,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# get_results_2026 — data fetcher
# ---------------------------------------------------------------------------


def get_results_2026(cat: str, code: str) -> dict[str, Any]:
    """Mirror of PHP ``get_results_2026($cat, $code)``.

    Returns ``{"summary_data", "inprocess", "exists", "missing"}`` where:
      - ``inprocess`` is a dict[title -> in_process row dict]
      - ``exists``    is a dict[title -> exists row dict] with ``via`` set
      - ``missing``   is a list[missing row dict] (in DB order)
    """
    # logic from results_2026/get_results_2026.php — exists_via_td
    pages_service = PagesService()
    exists_via_td_rows = pages_service.list_pages_by_lang_cat(code, cat)
    exists_via_td = {p.title: p for p in exists_via_td_rows}

    result_2026_service = Results2026Service()
    items_missing = result_2026_service.missing_by_lang_and_category(code, cat)
    missing_by_title = {row["title"]: row for row in items_missing if row.get("title")}
    items_exists_list = result_2026_service.exists_by_lang_and_category(code, cat)
    items_exists: dict[str, dict] = {row["title"]: row for row in items_exists_list}

    # Tag each exists row with via="td" or via="before" — PHP foreach loop.
    for title, row in items_exists.items():
        row["via"] = "td" if title in exists_via_td else "before"

    # logic from results_2026/get_results_2026.php — getinprocess_n
    missing_titles = {row["title"] for row in items_missing}
    inprocess = get_inprocess_for_missing(missing_titles, code)

    # Remove inprocess titles from missing.
    if inprocess:
        inprocess_titles = set(inprocess.keys())
        items_missing = [m for m in items_missing if m["title"] not in inprocess_titles]

    summary_data = {
        "code": code,
        "cat": cat,
        "len_inprocess": len(inprocess),
        "len_missing": len(items_missing),
        "len_exists": len(items_exists),
        "total": len(items_exists) + len(items_missing) + len(inprocess),
    }
    # Match PHP ksort($items_exists)
    items_exists = dict(sorted(items_exists.items()))

    return {
        "summary_data": summary_data,
        "inprocess": inprocess,
        "exists": items_exists,
        "missing": items_missing,
        "missing_by_title": missing_by_title,
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def results_loader_2026(
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
    """Build the results bundle for the index page.

    Mirrors PHP ``results_loader_2026($data)`` + ``Results_tables_2026(...)``.
    Returns a :class:`ResultsBundle` with the data the Jinja templates need;
    produces no HTML side effects of its own.
    """
    # logic from results_2026/get_results_2026.php
    bucket = get_results_2026(cat, code)

    # logic from results_2026/index.php — load_translate_type('no'|'full')
    nolead_titles, full_titles = load_translate_type_sets()

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

    missing_rows = build_missing_rows(
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

    inprocess_rows = build_inprocess_rows(
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

    exists_rows, exists_translated_count, exists_translated_before_count = build_exists_rows(
        exists=bucket["exists"],
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
    "get_results_2026",
    "results_loader_2026",
]
