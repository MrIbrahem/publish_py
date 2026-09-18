r"""Port of ``results_27/Data/ResultsFetcher.php``.

Responsible for fetching and preparing all result data (exists, missing,
in-process) for a given category and language. Mirrors PHP
``Results\GetResults27\Data\ResultsFetcher::get()``; produces no HTML.
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


class ResultsFetcher:
    """Fetch and partition the exists/missing/in-process data for one category."""

    def get(self, cat: str, code: str) -> dict[str, Any]:
        """Return ``{"summary_data", "inprocess", "exists", "missing"}``.

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
        items_exists_list = result_2026_service.exists_by_lang_and_category(code, cat)
        items_exists: dict[str, dict] = {row["title"]: row for row in items_exists_list}

        # Tag each exists row with via="td" or via="before" — PHP foreach loop.
        for title, row in items_exists.items():
            row["via"] = "td" if title in exists_via_td else "before"

        # logic from results_2026/get_results_2026.php — getinprocess_n
        missing_titles = {row["title"] for row in items_missing}
        inprocess = self._get_in_process(missing_titles, code)

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
        }

    def _get_in_process(self, missing_titles: set[str], code: str) -> dict[str, dict]:
        """Mirror of PHP ``getinprocess_n($missing, $code)``.

        Keeps only the in-process records whose title is still in the missing
        list.
        """
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


def get_results_27(cat: str, code: str) -> dict[str, Any]:
    """Backward-compatible wrapper around :class:`ResultsFetcher`.

    Mirrors PHP ``get_results_27($cat, $code)``.
    """
    return ResultsFetcher().get(cat, code)


__all__ = [
    "ResultsFetcher",
    "get_results_27",
]
