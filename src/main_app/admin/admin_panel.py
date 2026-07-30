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

from .decorators import admin_required
from .routes.categories import categories_dashboard
from .routes.last import last_translations_dashboard
from .sidebar import create_side

logger = logging.getLogger(__name__)


class AdminPanel:
    """admin panel routes."""

    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:

        @self.bp.app_context_processor
        def inject_sidebar() -> dict[str, Any]:
            path_parts = request.path.strip("/").split("/")
            active_route = path_parts[1] if len(path_parts) > 1 else ""
            # logger.debug(f"Injecting sidebar for path='{request.path}', {active_route=}")
            sidebar_html = create_side(active_route=active_route, path=request.path)
            return {"sidebar": sidebar_html}

        self.bp.route("/", methods=["GET"])(admin_required(self.index))
        self.bp.route("/last", methods=["GET"])(admin_required(self.last_dashboard))
        self.bp.route("/last/pages/<string:lang>", methods=["GET"])(admin_required(self.dashboard_pages))
        self.bp.add_url_rule(
            "/last/pages/",
            endpoint="dashboard_pages_default",
            view_func=admin_required(self.dashboard_pages),
            methods=["GET"],
        )
        self.bp.route("/last/pages_users/<string:lang>", methods=["GET"])(admin_required(self.dashboard_pages_users))
        self.bp.add_url_rule(
            "/last/pages_users/",
            endpoint="dashboard_pages_users_default",
            view_func=admin_required(self.dashboard_pages_users),
            methods=["GET"],
        )
        self.bp.route("/reports", methods=["GET"])(admin_required(self.reports))
        self.bp.route("/process", methods=["GET"])(admin_required(self.in_process_dashboard))
        self.bp.route("/process_total", methods=["GET"])(admin_required(self.in_process_total_dashboard))
        self.bp.route("/edit_done", methods=["GET"])(admin_required(self.edit_done))
        self.bp.route("/categories", methods=["GET"])(admin_required(self.categories_dashboard_route))

    def index(self):
        return redirect(url_for("admin.last_dashboard"))

    def last_dashboard(self) -> Response:
        # Get query parameters
        lang = request.args.get("lang", "All", type=str)
        last_table = request.args.get("last_table", "pages", type=str)

        # Validate last_table
        if last_table == "pages_users":
            return redirect(url_for("admin.dashboard_pages_users", lang=lang))
        else:
            return redirect(url_for("admin.dashboard_pages", lang=lang))

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
