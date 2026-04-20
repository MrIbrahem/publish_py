"""Admin-only routes for viewing in-process translation totals by user."""

from __future__ import annotations

import logging

from flask import Blueprint, render_template

from ..decorators import admin_required
from ...public.services.in_process_service import get_in_process_counts_by_user

logger = logging.getLogger(__name__)


def _in_process_total_dashboard():
    """Render the in-process totals dashboard."""

    user_counts = get_in_process_counts_by_user()
    total_users = len(user_counts)
    total_articles = sum(user["article_count"] for user in user_counts)

    return render_template(
        "admins/in_process_total.html",
        user_counts=user_counts,
        total_users=total_users,
        total_articles=total_articles,
    )


class InProcessTotal:
    def __init__(self, bp_admin: Blueprint):
        @bp_admin.get("/process_total")
        @admin_required
        def in_process_total_dashboard():
            return _in_process_total_dashboard()
