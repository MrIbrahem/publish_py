"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    current_app,
    render_template,
    send_from_directory,
)
from flask.views import MethodView
from flask.wrappers import Response

logger = logging.getLogger(__name__)


class MainIndexView(MethodView):
    """Render the application homepage."""

    def get(self) -> str:
        """Serve the landing page."""
        return render_template(
            "index.html",
        )


class MainReportsView(MethodView):
    """Render the reports page."""

    def get(self) -> str:
        """Serve the reports page."""
        return render_template(
            "reports.html",
        )


class MainFaviconView(MethodView):
    """Serve the site favicon."""

    def get(self) -> Response:
        """Stream ``favicon.ico`` from the static folder."""
        return send_from_directory(current_app.static_folder, "favicon.ico", mimetype="image/x-icon")  # type: ignore


class MainRoutes:
    """Registrar for the main application views."""

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the homepage, reports and favicon views."""
        bp.add_url_rule("/", view_func=MainIndexView.as_view("index"))
        bp.add_url_rule("/reports", view_func=MainReportsView.as_view("reports"))
        bp.add_url_rule("/favicon.ico", view_func=MainFaviconView.as_view("favicon"))


__all__ = [
    "MainRoutes",
]
