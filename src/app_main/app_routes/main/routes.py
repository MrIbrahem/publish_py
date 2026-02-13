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

from ...users.current import current_user

bp_main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


@bp_main.get("/")
def index():
    current_user_obj = current_user()
    return render_template(
        "index.html",
        current_user=current_user_obj,
    )


@bp_main.get("/reports")
def reports():
    current_user_obj = current_user()
    return render_template(
        "reports.html",
        current_user=current_user_obj,
    )


@bp_main.get("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/x-icon")


__all__ = ["bp_main"]
