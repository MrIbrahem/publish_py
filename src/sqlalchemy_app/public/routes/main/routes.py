"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    flash,
    render_template,
    request,
    send_from_directory,
)

from ....shared.services.category_service import list_categories
from ....shared.services.lang_service import list_langs

bp_main = Blueprint("main", __name__, url_prefix="")
logger = logging.getLogger(__name__)


@bp_main.get("/")
def index():
    langs = [x.to_dict() for x in list_langs()]
    campaigns = list_categories()
    campaigns_list = [x.to_dict() for x in campaigns]
    camp = request.args.get("camp")

    camp_to_cats = [c.campaign for c in campaigns if c.campaign]
    if camp and camp not in camp_to_cats:
        flash(f"Campaign: {camp} is not valid campaign", "danger")

    langs_dict = {x["code"]: x for x in langs}
    code = request.args.get("code")
    lang_name = langs_dict.get(code, {}).get("name")

    if code and not lang_name:
        flash(f"Code: {code} is not valid wiki", "danger")

    tr_type = request.args.get("type")

    return render_template(
        "index.html",
        settings={
            "allow_whole_translate": True,
        },
        langs=langs,
        campaigns=campaigns_list,
        args={
            "code": code,
            "camp": camp,
            "type": tr_type,
        },
    )


@bp_main.get("/reports")
def reports():
    return render_template(
        "reports.html",
    )


@bp_main.get("/missing")
def missing():
    return render_template(
        "missing.html",
    )


@bp_main.get("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/x-icon")


__all__ = ["bp_main"]
