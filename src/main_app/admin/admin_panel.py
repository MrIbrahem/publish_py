"""Admin-only routes for managing coordinator access."""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)

from .decorators import admin_required
from .routes.categories import categories_dashboard
from .routes.last import last_translations_dashboard
from .sidebar import create_side

logger = logging.getLogger(__name__)


class AdminPanelRoutes:
    """admin panel routes."""

    def __init__(self) -> None:
        self.bp = Blueprint("admin", __name__, url_prefix="/admin")
        self._setup_routes()

    def _setup_routes(self) -> None:

        @self.bp.route("/", methods=["GET"])
        @admin_required
        def index():
            return redirect(url_for("admin.last_dashboard"))

        @self.bp.route("/last", methods=["GET"])
        @admin_required
        def last_dashboard():
            # Get query parameters
            lang = request.args.get("lang", "All", type=str)

            last_table = request.args.get("last_table", "pages", type=str)

            # Validate last_table
            if last_table not in ["pages", "pages_users"]:
                last_table = "pages"

            return last_translations_dashboard(last_table, lang)

        @self.bp.route("/last/pages/<string:lang>", methods=["GET"])
        @self.bp.route("/last/pages/", methods=["GET"])
        @admin_required
        def dashboard_pages(lang : str | None = None):
            return last_translations_dashboard("pages", lang)

        @self.bp.route("/last/pages_users/<string:lang>", methods=["GET"])
        @self.bp.route("/last/pages_users/", methods=["GET"])
        @admin_required
        def dashboard_pages_users(lang : str | None = None):
            return last_translations_dashboard("pages_users", lang)

        @self.bp.route("/reports", methods=["GET"])
        @admin_required
        def reports():
            return render_template("admins/reports.html")

        @self.bp.route("/process", methods=["GET"])
        @admin_required
        def in_process_dashboard():
            return render_template("admins/in_process.html")

        @self.bp.route("/process_total", methods=["GET"])
        @admin_required
        def in_process_total_dashboard():
            """
            Render the in-process totals dashboard.

            This route load data using DataTable ajax to API endpoint: `/api/in_process_total`
            """
            return render_template("admins/in_process_total.html")

        @self.bp.route("/edit_done", methods=["GET"])
        @admin_required
        def edit_done() -> str:
            return render_template("admins/close_btn.html")

        @self.bp.route("/categories", methods=["GET"])
        @admin_required
        def categories_dashboard_route():
            return categories_dashboard()

        @self.bp.app_context_processor
        def inject_sidebar():
            path_parts = request.path.strip("/").split("/")
            active_route = path_parts[1] if len(path_parts) > 1 else ""
            # logger.debug(f"Injecting sidebar for path='{request.path}'")
            sidebar_html = create_side(active_route=active_route)
            return {"sidebar": sidebar_html}


admin_route_module = AdminPanelRoutes()


__all__ = [
    "admin_route_module",
]
