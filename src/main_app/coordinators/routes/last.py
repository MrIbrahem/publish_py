"""
Coordinator-only routes for recent translations (last).
"""

from __future__ import annotations

import logging

from flask import render_template

from ...database.services import CategoryService, LangService, PagesQueryService
from .last_mapping import LastRow

logger = logging.getLogger(__name__)


def add_campaigns(rows: list[LastRow]) -> None:
    category_service = CategoryService()
    camps = category_service.get_camp_to_cats()
    cats_to_camp = {v: x for x, v in camps.items() if v}

    for row in rows:
        row.add_campaign(cats_to_camp)


class LastTranslationsDashboard:
    """Render the last-translated pages table."""

    @staticmethod
    def load_rows(last_table: str, lang: str) -> list[LastRow]:
        # Fetch data based on table type
        service = PagesQueryService()

        if last_table == "pages":
            raw_rows = service.list_pages_with_views(limit=100, lang=lang)
        else:
            raw_rows = service.list_pages_users(limit=100, lang=lang)

        rows = [LastRow.from_row(row=r, last_table=last_table) for r in raw_rows]

        add_campaigns(rows)
        return rows

    @classmethod
    def dashboard(cls, last_table: str, lang: str | None = None) -> str:
        """Render the recent translations dashboard."""
        lang = lang or "All"
        rows = cls.load_rows(last_table, lang)

        # Get languages for dropdown
        lang_service = LangService()
        languages = lang_service.list_langs()

        return render_template(
            "coordinators/last/index.html",
            rows=rows,
            languages=languages,
            current_lang=lang or "All",
            last_table=last_table,
            count=len(rows),
        )


__all__ = [
    "LastTranslationsDashboard",
]
