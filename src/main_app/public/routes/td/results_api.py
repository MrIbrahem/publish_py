"""
Results API — mirrors PHP Results/GetResults/get_results_new.
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

from ....database.services import (
    AllQidsService,
    CategoryMemberService,
    CategoryService,
    InProcessService,
    PagesService,
)

logger = logging.getLogger(__name__)

class ResultsApiService:
    """Service for computing Translation Dashboard results."""

    def __init__(
        self,
        category_service: CategoryService | None = None,
        pages_service: PagesService | None = None,
        category_member_service: CategoryMemberService | None = None,
        all_qids_service: AllQidsService | None = None,
        in_process_service: InProcessService | None = None,
    ) -> None:
        self.category_service = category_service or CategoryService()
        self.pages_service = pages_service or PagesService()
        self.category_member_service = category_member_service or CategoryMemberService()
        self.all_qids_service = all_qids_service or AllQidsService()
        self.in_process_service = in_process_service or InProcessService()

    def resolve_campaign_to_category(self, camp: str) -> str:
        cats = self.category_service.get_camp_to_cats()
        return cats.get(camp, camp)

    def get_cat_exists_and_missing(
        self,
        pages_by_title: dict[str, Any],
        cat: str,
        code: str,
    ) -> tuple[dict, list]:
        if not pages_by_title:
            pages_by_title = {p.title: p for p in self.pages_service.list_pages_by_lang_cat(code, cat)}

        members = self.category_member_service.get_members_by_category(cat)
        member_set = {x.article_id for x in members}

        exists = {}
        for title, page in pages_by_title.items():
            if title in member_set:
                exists[title] = {
                    "qid": getattr(page, "qid", "") or "",
                    "title": page.title or "",
                    "target": page.target or "",
                    "via": "td",
                    "pupdate": page.pupdate or "",
                    "user": page.user or "",
                }

        missing = list(member_set - set(exists.keys()))

        return exists, missing

    def get_exists_targets_by_lang(self, lang: str) -> dict[str, dict]:
        rows = self.all_qids_service.list_targets_by_lang(lang)
        result = {row["title"]: row for row in rows}
        return result

    @staticmethod
    def exists_expends(
        missing: list[str],
        targets: dict[str, dict],
    ) -> dict[str, dict]:
        result = {}
        for title in missing:
            entry = targets.get(title)
            if entry and entry.get("target"):
                result[title] = {
                    "qid": entry.get("qid", ""),
                    "title": entry.get("title", ""),
                    "target": entry["target"],
                    "via": "before",
                }
        return result

    def get_inprocess_for_titles(self, missing: list[str], code: str) -> dict[str, dict]:
        records = self.in_process_service.list_in_process_by_lang(code)

        missing_set = set(missing)
        return {
            r.title: {
                "id": r.id,
                "title": r.title,
                "user": r.user,
                "lang": r.lang,
                "cat": r.cat,
                "translate_type": r.translate_type,
                "word": r.word,
                "add_date": r.add_date.isoformat() if r.add_date else None,
            }
            for r in records
            if r.title in missing_set
        }

    @staticmethod
    def unique_ordered(items: list[str]) -> list[str]:
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def make_mdwiki_cat_url(category: str, name: str | None = None) -> str:
        if not category:
            return ""
        clean = category.replace("Category:", "")
        display = name or clean

        encoded = quote(clean.replace(" ", "_"), safe="")
        return f"<a target='_blank' href='https://mdwiki.org/wiki/Category:{encoded}'>{display}</a>"

    def get_results(
        self,
        code: str | None,
        camp: str | None,
        cat2: str | None = None,
    ) -> dict[str, Any]:
        code = code or "ar"
        camp = camp or "Hearing"

        cat = self.resolve_campaign_to_category(camp)

        pages = self.pages_service.list_pages_by_lang_cat(code, cat)
        pages_by_title = {p.title: p for p in pages}

        items_exists, items_missing = self.get_cat_exists_and_missing(pages_by_title, cat, code)

        targets = self.get_exists_targets_by_lang(code)
        extra_exists = self.exists_expends(items_missing, targets)

        if extra_exists:
            items_exists.update(extra_exists)
            items_missing = [t for t in items_missing if t not in extra_exists]

        missing = self.unique_ordered(items_missing)

        inprocess = self.get_inprocess_for_titles(missing, code)
        in_titles = set(inprocess)
        missing = [t for t in missing if t not in in_titles]

        summary_data = {
            "code": code,
            "cat": cat,
            "len_inprocess": len(inprocess),
            "len_missing": len(missing),
            "len_exists": len(items_exists),
            "total": len(items_exists) + len(missing) + len(inprocess),
        }
        return {
            "summary_data": summary_data,
            "inprocess": inprocess,
            "exists": dict(sorted(items_exists.items())),
            "missing": missing,
        }


def results_api_result(
    code: str | None,
    camp: str | None,
    cat2: str | None = None,
) -> dict[str, Any]:
    return ResultsApiService().get_results(code, camp, cat2)


__all__ = [
    "ResultsApiService",
    "results_api_result",
]
