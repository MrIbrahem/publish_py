"""
Admin-only routes for recent translations (last).
"""

from __future__ import annotations

import logging
from typing import Any

from flask import render_template

from ...database.services import CategoryService, LangService, PagesQueryService

logger = logging.getLogger(__name__)


def add_campaign(
    rows: list[dict[str, Any]],
    cats_to_camp: dict[str, str],
) -> list[dict[str, Any]]:
    last_rows = []
    for row in rows:
        cat = row.get("cat")
        campaign = row.get("campaign")
        if not campaign and cat:
            campaign = cats_to_camp.get(cat)
        row["campaign"] = campaign
        last_rows.append(row)
    return last_rows


def last_translations_dashboard(
    last_table: str,
    lang: str | None = None,
) -> str:
    """Render the recent translations dashboard."""
    if lang is None:
        lang = "All"

    # Fetch data based on table type
    service = PagesQueryService()
    if last_table == "pages":
        rows = service.list_pages_with_views(limit=100, lang=lang)
    else:
        rows = service.list_pages_users(limit=100, lang=lang)

    category_service = CategoryService()
    camps = category_service.get_camp_to_cats()
    cats_to_camp = {v: x for x, v in camps.items() if v}

    last_rows = add_campaign(rows, cats_to_camp)

    # Get languages for dropdown
    lang_service = LangService()
    languages = lang_service.list_langs()

    return render_template(
        "admins/last/index.html",
        rows=last_rows,
        languages=languages,
        current_lang=lang,
        last_table=last_table,
        count=len(last_rows),
    )


__all__ = [
    "last_translations_dashboard",
]
