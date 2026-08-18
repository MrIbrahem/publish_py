"""Admin-only routes for managing coordinator access."""

from __future__ import annotations

import logging
from typing import Any

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.wrappers.response import Response

from ..templates_markups import create_side
from .decorators import admin_required
from .routes.categories import categories_dashboard
from .routes.last import last_translations_dashboard

logger = logging.getLogger(__name__)


class AdminPanel:
    """admin panel routes."""

    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:

        self.bp.app_context_processor(self.inject_sidebar)

        routes = [
            ("/", "GET", self.index),
            ("/last", "GET", self.last_dashboard),
            ("/last/pages/<string:lang>", "GET", self.dashboard_pages),
            ("/last/pages_users/<string:lang>", "GET", self.dashboard_pages_users),
            ("/reports", "GET", self.reports),
            ("/process", "GET", self.in_process_dashboard),
            ("/process_total", "GET", self.in_process_total_dashboard),
            ("/edit_done", "GET", self.edit_done),
            ("/categories", "GET", self.categories_dashboard_route),
        ]
        for rule, method, target in routes:
            self.bp.route(rule, methods=[method])(admin_required(target))

        self.bp.add_url_rule(
            "/last/pages/",
            endpoint="dashboard_pages_default",
            view_func=admin_required(self.dashboard_pages),
            methods=["GET"],
        )
        self.bp.add_url_rule(
            "/last/pages_users/",
            endpoint="dashboard_pages_users_default",
            view_func=admin_required(self.dashboard_pages_users),
            methods=["GET"],
        )

    def inject_sidebar(self) -> dict[str, Any]:
        return {"create_side": create_side}

    def index(self):
        return redirect(url_for("adminpanel.last_dashboard"))

    def last_dashboard(self) -> Response:
        # Get query parameters
        lang = request.args.get("lang", "All", type=str)
        last_table = request.args.get("last_table", "pages", type=str)

        # Validate last_table
        if last_table == "pages_users":
            return redirect(url_for("adminpanel.dashboard_pages_users", lang=lang))
        else:
            return redirect(url_for("adminpanel.dashboard_pages", lang=lang))

    def dashboard_pages(self, lang: str | None = None):
        return last_translations_dashboard("pages", lang)

    def dashboard_pages_users(self, lang: str | None = None):
        return last_translations_dashboard("pages_users", lang)

    def reports(self):
        return render_template("admins/reports.html")

    def in_process_dashboard(self):
        return render_template("admins/in_process.html")

    def in_process_total_dashboard(self):
        """
        Render the in-process totals dashboard.

        This route load data using DataTable ajax to API endpoint: `/api/in_process_total`
        """
        return render_template("admins/in_process_total.html")

    def edit_done(self) -> str:
        return render_template("admins/close_btn.html")

    def categories_dashboard_route(self):
        return categories_dashboard()


__all__ = [
    "AdminPanel",
]
