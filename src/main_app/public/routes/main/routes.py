"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    render_template,
    send_from_directory,
)
from flask.wrappers import Response

logger = logging.getLogger(__name__)


class MainRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(self.index)
        self.bp.route("/reports", methods=["GET"])(self.reports)
        self.bp.get("/favicon.ico")(self.favicon)

    def index(self) -> str:
        return render_template(
            "index.html",
        )

    def reports(self):
        return render_template(
            "reports.html",
        )

    def favicon(self) -> Response:
        return send_from_directory("static", "favicon.ico", mimetype="image/x-icon")


__all__ = [
    "MainRoutes",
]
