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

from ....shared.services.lang_service import list_langs

bp_main = Blueprint("main", __name__, url_prefix="")
logger = logging.getLogger(__name__)


@bp_main.get("/")
def index():
    lang_tables = [x.to_dict() for x in list_langs()]
    return render_template(
        "index.html",
        lang_tables=lang_tables,
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
