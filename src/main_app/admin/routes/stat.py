"""Admin route for the statistics dashboard (stub).

No PHP source exists for this dashboard; this implementation provides a
placeholder index page that displays simple counts of ``pages`` and
``pages_users`` rows.
"""

from __future__ import annotations

import logging

from flask import Blueprint, render_template

from ...db.services import PagesService, UserPagesService

logger = logging.getLogger(__name__)


class StaticsRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.user_pages_service = UserPagesService()
        self.pages_service = PagesService()
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(self.stat_index)

    def stat_index(self) -> str:
        """Render a minimal statistics overview."""
        try:
            pages_count = self.pages_service.count_translated()
        except Exception:
            logger.exception("Failed to count translated pages")
            pages_count = None

        try:
            user_pages_count = self.user_pages_service.count_translated()
        except Exception:
            logger.exception("Failed to count translated user pages")
            user_pages_count = None

        return render_template(
            "admins/stat.html",
            pages_count=pages_count,
            user_pages_count=user_pages_count,
        )


__all__ = [
    "StaticsRoutes",
]
