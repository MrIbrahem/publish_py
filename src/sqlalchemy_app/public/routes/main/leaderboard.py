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

from ....shared.auth.identity import current_user

bp_leaderboard = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")
logger = logging.getLogger(__name__)


@bp_leaderboard.get("/")
def index():
    current_user_obj = current_user()
    return render_template(
        "index.html",
        current_user=current_user_obj,
    )


@bp_leaderboard.get("/reports")
def reports():
    current_user_obj = current_user()
    return render_template(
        "reports.html",
        current_user=current_user_obj,
    )


@bp_leaderboard.get("/leaderboard")
def leaderboard():
    current_user_obj = current_user()
    return render_template(
        "leaderboard.html",
        current_user=current_user_obj,
    )


@bp_leaderboard.get("/missing")
def missing():
    current_user_obj = current_user()
    return render_template(
        "missing.html",
        current_user=current_user_obj,
    )


@bp_leaderboard.get("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/x-icon")


__all__ = ["bp_leaderboard"]
