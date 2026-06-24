"""
Admin-only routes for recent translations (last).
"""

from __future__ import annotations

import logging

from flask import render_template

from ...db.services.content import get_camp_to_cats, list_langs
from ...db.services.pages_query_service import list_pages_users, list_pages_with_views

logger = logging.getLogger(__name__)


def add_campaign(rows, cats_to_camp):
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

    # Fetch data based on table type
    if last_table == "pages":
        rows = list_pages_with_views(limit=100, lang=lang)
    else:
        rows = list_pages_users(limit=100, lang=lang)

    camps = get_camp_to_cats()
    cats_to_camp = {v: x for x, v in camps.items() if v}

    last_rows = add_campaign(rows, cats_to_camp)

    # Get languages for dropdown
    languages = list_langs()

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
