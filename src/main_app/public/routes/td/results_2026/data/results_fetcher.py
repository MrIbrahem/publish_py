"""
Port of ``ResultsFetcher.php``.

Responsible for fetching and preparing all result data (exists, missing,
in-process) for a given category and language. Mirrors PHP
``ResultsFetcher::get()``; produces no HTML.
"""

from __future__ import annotations

import logging
from typing import Any

from ......database.services import (
    InProcessService,
    PagesService,
    Results2026Service,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# data fetcher
# ---------------------------------------------------------------------------


class ResultsFetcher:
    """Fetch and partition the exists/missing/in-process data for one category."""

    def __init__(self) -> None:
        self.pages_service = PagesService()
        self.result_2026_service = Results2026Service()
        self.in_process_service = InProcessService()

    def get(self, cat: str, code: str) -> dict[str, Any]:
        """
        Returns ``{"summary_data", "inprocess", "exists", "missing"}`` where:
        - ``inprocess`` is a dict[title -> in_process row dict]
        - ``exists``    is a dict[title -> exists row dict] with ``via`` set
        - ``missing``   is a list[missing row dict] (in DB order)
        """
        # logic from results_2026/get_results_2026.php — exists_via_td
        exists_via_td_rows = self.pages_service.list_pages_by_lang_cat(code, cat)
        exists_via_td = {p.title: p for p in exists_via_td_rows}

        items_missing = self.result_2026_service.missing_by_lang_and_category(code, cat)
        missing_by_title = {row["title"]: row for row in items_missing if row.get("title")}

        items_exists_list = self.result_2026_service.exists_by_lang_and_category(code, cat)
        items_exists: dict[str, dict] = {row["title"]: row for row in items_exists_list}

        # Tag each exists row with via="td" or via="before" — PHP foreach loop.
        for title, row in items_exists.items():
            row["via"] = "td" if title in exists_via_td else "before"

        # logic from results_2026/get_results_2026.php — getinprocess_n
        inprocess = self.get_inprocess_for_missing(missing_by_title, code)

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

    def get_inprocess_for_missing(self, missing_by_title: dict[str, dict], code: str) -> dict[str, dict]:
        """
        Mirror of PHP ``getinprocess_n($missing, $code)``.

        Keeps only the in-process records whose title is still in the missing
        list.
        """

        records = self.in_process_service.list_in_process_by_lang(code)
        result: dict[str, dict] = {}

        for r in records:
            if r.title not in missing_by_title:
                continue

            result[r.title] = r.to_json()
            """
            c.article_id   AS title,
            c.category     AS category,
            ase.importance AS importance,
            rc.r_lead_refs AS r_lead_refs,
            rc.r_all_refs  AS r_all_refs,
            ep.en_views    AS en_views,
            q.qid          AS qid,
            w.w_lead_words AS w_lead_words,
            w.w_all_words  AS w_all_words"""
            result[r.title].update({x:v for x, v in missing_by_title[r.title].items() if x not in result[r.title]})

        return result


__all__ = [
    "ResultsFetcher",
]
