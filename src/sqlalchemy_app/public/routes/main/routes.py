"""
Defines the main routes for the application, such as the homepage.
"""

from __future__ import annotations

import logging
import time

from flask import (
    Blueprint,
    flash,
    jsonify,
    render_template,
    request,
    send_from_directory,
)

from ....shared.services.category_service import list_categories
from ....shared.services.lang_service import list_langs
from .results_api import results_api_result

bp_main = Blueprint("main", __name__, url_prefix="")
logger = logging.getLogger(__name__)


@bp_main.get("/results_api")
def results_api():
    code = request.args.get("code")
    camp = request.args.get("camp")
    depth = request.args.get("depth")

    start = time.time()
    result_dict = results_api_result(code, camp, depth)
    elapsed = time.time() - start

    return jsonify(
        {
            "execution_time": round(elapsed, 6),
            "results": result_dict,
        }
    )


@bp_main.get("/")
def index():
    langs = [x.to_dict() for x in list_langs()]
    langs_dict = {x["code"]: x for x in langs}
    campaigns = [x.to_dict() for x in list_categories()]

    code = request.args.get("code")
    camp = request.args.get("camp")
    translate_type = request.args.get("type")
    lang_name = langs_dict.get(code, {}).get("name")

    if code and not lang_name:
        flash(f"Code: {code} is not valid wiki", "danger")

    return render_template(
        "index.html",
        settings={
            "allow_whole_translate": True,
        },
        langs=langs,
        campaigns=campaigns,
        args={
            "code": code,
            "camp": camp,
            "type": translate_type,
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
