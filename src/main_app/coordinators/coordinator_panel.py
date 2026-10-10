"""Coordinator-only routes for the admin dashboard, built on MethodView."""

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
from flask.views import MethodView
from werkzeug.wrappers.response import Response

from ..templates_markups import create_side
from .decorators import coordinator_required
from .routes.categories import categories_dashboard
from .routes.last import last_translations_dashboard

logger = logging.getLogger(__name__)


class BaseCoordinatorPanelView(MethodView):
    """Base view for the Coordinator Panel pages.

    Every Coordinator Panel page requires an authenticated administrator, so
    ``coordinator_required`` is declared here and inherited by all subclasses.
    """

    decorators = [coordinator_required]


class CoordinatorPanelIndexView(BaseCoordinatorPanelView):
    """Redirect the panel root to the last-translations dashboard."""

    def get(self) -> Response:
        """Redirect to the last dashboard."""
        return redirect(url_for("coordinators_panel.last_dashboard"))


class CoordinatorPanelLastDashboardView(BaseCoordinatorPanelView):
    """Dispatch the "last translations" landing page to the right table."""

    def get(self) -> Response:
        """Read ``last_table`` and redirect to the matching dashboard."""
        # Get query parameters
        lang = request.args.get("lang", "All", type=str)
        last_table = request.args.get("last_table", "pages", type=str)

        # Validate last_table
        if last_table == "pages_users":
            return redirect(url_for("coordinators_panel.dashboard_pages_users", lang=lang))
        else:
            return redirect(url_for("coordinators_panel.dashboard_pages", lang=lang))


class CoordinatorPanelPagesView(BaseCoordinatorPanelView):
    """Render the last-translated pages table."""

    def get(self, lang: str | None = None) -> str:
        """Render the ``pages`` last-translations dashboard."""
        return last_translations_dashboard("pages", lang)


class CoordinatorPanelPagesUsersView(BaseCoordinatorPanelView):
    """Render the last-translated userspace pages table."""

    def get(self, lang: str | None = None) -> str:
        """Render the ``pages_users`` last-translations dashboard."""
        return last_translations_dashboard("pages_users", lang)


class CoordinatorPanelReportsView(BaseCoordinatorPanelView):
    """Render the admin reports page."""

    def get(self) -> str:
        """Render the reports page."""
        return render_template("coordinators/reports.html")


class CoordinatorPanelInProcessView(BaseCoordinatorPanelView):
    """Render the in-process translations dashboard."""

    def get(self) -> str:
        """Render the in-process page."""
        return render_template("coordinators/in_process.html")


class CoordinatorPanelInProcessTotalView(BaseCoordinatorPanelView):
    """Render the in-process totals dashboard."""

    def get(self) -> str:
        """
        Render the in-process totals dashboard.

        This route load data using DataTable ajax to API endpoint: `/api/in_process_total`
        """
        return render_template("coordinators/in_process_total.html")


class CoordinatorPanelEditDoneView(BaseCoordinatorPanelView):
    """Render the "edit done" confirmation fragment."""

    def get(self) -> str:
        """Render the close-button fragment."""
        return render_template("coordinators/close_btn.html")


class CoordinatorPanelCategoriesView(BaseCoordinatorPanelView):
    """Render the categories dashboard."""

    def get(self) -> str:
        """Render the categories dashboard page."""
        return categories_dashboard()


class CoordinatorPanel:
    """Coordinator Panel routes registrar using class-based views."""

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the Coordinator Panel views on the blueprint.

        Endpoint names (``index``, ``last_dashboard``, ``dashboard_pages``,
        ...) are preserved from the legacy function-based routes so
        existing ``url_for('coordinators_panel.edit_done')`` calls keep resolving.
        """
        bp.app_context_processor(cls.inject_sidebar)

        bp.add_url_rule("/", view_func=CoordinatorPanelIndexView.as_view("index"), methods=["GET"])
        bp.add_url_rule("/last", view_func=CoordinatorPanelLastDashboardView.as_view("last_dashboard"), methods=["GET"])
        bp.add_url_rule(
            "/last/pages/<string:lang>", view_func=CoordinatorPanelPagesView.as_view("dashboard_pages"), methods=["GET"]
        )
        bp.add_url_rule(
            "/last/pages_users/<string:lang>",
            view_func=CoordinatorPanelPagesUsersView.as_view("dashboard_pages_users"),
            methods=["GET"],
        )
        bp.add_url_rule("/reports", view_func=CoordinatorPanelReportsView.as_view("reports"), methods=["GET"])
        bp.add_url_rule(
            "/process", view_func=CoordinatorPanelInProcessView.as_view("in_process_dashboard"), methods=["GET"]
        )
        bp.add_url_rule(
            "/process_total",
            view_func=CoordinatorPanelInProcessTotalView.as_view("in_process_total_dashboard"),
            methods=["GET"],
        )
        bp.add_url_rule("/edit_done", view_func=CoordinatorPanelEditDoneView.as_view("edit_done"), methods=["GET"])
        bp.add_url_rule(
            "/categories",
            view_func=CoordinatorPanelCategoriesView.as_view("categories_dashboard_route"),
            methods=["GET"],
        )

        # ------------------------------------------------------------------
        # TODO: Backward Compatibility / Temporary Aliases
        # Legacy language-less "default" endpoints for the last dashboards.
        # Remove these rules once all template forms and url_for calls are
        # updated to pass a language.
        # ------------------------------------------------------------------
        bp.add_url_rule(
            "/last/pages/",
            endpoint="dashboard_pages_default",
            view_func=CoordinatorPanelPagesView.as_view("legacy_dashboard_pages_default"),
            methods=["GET"],
        )
        bp.add_url_rule(
            "/last/pages_users/",
            endpoint="dashboard_pages_users_default",
            view_func=CoordinatorPanelPagesUsersView.as_view("legacy_dashboard_pages_users_default"),
            methods=["GET"],
        )

    @staticmethod
    def inject_sidebar() -> dict[str, Any]:
        """Provide the admin sidebar markup as a template global."""
        return {"create_side": create_side}


__all__ = [
    "CoordinatorPanel",
]
