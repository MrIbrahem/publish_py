"""Admin-only routes for recent translations (last)."""

from __future__ import annotations

import logging

from flask import Blueprint, render_template, request

from ..decorators import admin_required
from ...public.services.lang_service import list_langs
from ...public.routes.api.pages_query_service import list_pages_with_views, list_pages_users

logger = logging.getLogger(__name__)


def _last_dashboard():
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


class LastDashboard:
    def __init__(self, bp_admin: Blueprint):
        @bp_admin.get("/last")
        @admin_required
        def last_dashboard():
            return _last_dashboard()
