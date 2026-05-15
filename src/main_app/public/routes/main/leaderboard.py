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
    return render_template(
        "leaderboard/index.html",
    )


@bp_leaderboard.get("/langs/<string:lang_code>")
def langs(lang_code: str):
    return render_template(
        "leaderboard/langs.html",
        lang_code=lang_code,
    )


@bp_leaderboard.get("/users/<string:username>")
def users(username: str):
    return render_template(
        "leaderboard/users.html",
        username=username,
    )


@bp_leaderboard.get("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/x-icon")


__all__ = ["bp_leaderboard"]
