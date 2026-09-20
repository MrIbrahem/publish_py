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
from flask.wrappers import Response

logger = logging.getLogger(__name__)


class MainRoutes:

    def register(self, bp: Blueprint) -> None:
        routes = [
            ("/", "GET", self.index),
            ("/reports", "GET", self.reports),
            ("/favicon.ico", "GET", self.favicon),
        ]
        for rule, method, target in routes:
            bp.route(rule, methods=[method])(target)

    def index(self) -> str:
        return render_template(
            "index.html",
        )

    def reports(self):
        return render_template(
            "reports.html",
        )

    def favicon(self) -> Response:
        return send_from_directory(current_app.static_folder, "favicon.ico", mimetype="image/x-icon")  # type: ignore


__all__ = [
    "MainRoutes",
]
