"""Admin-only routes for recent translations (last)."""

from __future__ import annotations

import logging

from flask import render_template, request

from ...public.routes.api.pages_query_service import list_pages_users, list_pages_with_views
from ...public.services.lang_service import list_langs

logger = logging.getLogger(__name__)


def last_translations_dashboard() -> str:
    """Render the recent translations dashboard."""

    # Get query parameters
    lang = request.args.get("lang", "All")
    last_table = request.args.get("last_table", "pages")

    # Validate last_table
    if last_table not in ["pages", "pages_users"]:
        last_table = "pages"

    # Fetch data based on table type
    if last_table == "pages":
        rows = list_pages_with_views(limit=100, lang=lang)
    else:
        rows = list_pages_users(limit=100, lang=lang)

    # Get languages for dropdown
    languages = list_langs()

    return render_template(
        "admins/last.html",
        rows=rows,
        languages=languages,
        current_lang=lang,
        last_table=last_table,
        count=len(rows),
    )
