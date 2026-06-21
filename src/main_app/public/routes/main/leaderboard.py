"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
)

from ....db.services import get_camp_to_cats, list_projects, get_pages_with_pupdate

bp_leaderboard = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")
logger = logging.getLogger(__name__)


@bp_leaderboard.get("/")
def index() -> str:
    campagins = get_camp_to_cats().keys()
    years = get_pages_with_pupdate()
    months = {}
    user_groups = [x.g_title for x in list_projects()]

    form_data = request.args
    return render_template(
        "leaderboard/index.html",
        campaigns=campagins,
        years=years,
        months=months,
        user_groups=user_groups,
        form=form_data,
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
