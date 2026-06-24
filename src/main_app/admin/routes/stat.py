"""Admin route for the statistics dashboard (stub).

No PHP source exists for this dashboard; this implementation provides a
placeholder index page that displays simple counts of ``pages`` and
``pages_users`` rows.
"""

from __future__ import annotations

import logging

from flask import Blueprint, render_template

from ..decorators import admin_required
from ...db.services.pages import page_service, user_page_service

logger = logging.getLogger(__name__)


stat_bp = Blueprint("stat", __name__, url_prefix="/stat")


@stat_bp.route("/", methods=["GET"])
@admin_required
def stat_index() -> str:
    """Render a minimal statistics overview."""
    try:
        pages_count = page_service.count_translated()
    except Exception:
        logger.exception("Failed to count translated pages")
        pages_count = 0

    try:
        user_pages_count = user_page_service.count_translated()
    except Exception:
        logger.exception("Failed to count translated user pages")
        user_pages_count = 0

    return render_template(
        "admins/stat.html",
        pages_count=pages_count,
        user_pages_count=user_pages_count,
    )
