"""Admin route for Translations add_translate dashboard."""

from __future__ import annotations

import logging

from flask import Blueprint, render_template, redirect

logger = logging.getLogger(__name__)


add_bp = Blueprint("add", __name__, url_prefix="/add")


@add_bp.route("/", methods=["POST"])
def add_translate_post() -> str:
    """Render the translations add_translate dashboard."""
    return redirect("admin.add_translate")


@add_bp.route("/", methods=["GET"])
def add_translate() -> str:
    """Render the translations add_translate dashboard."""
    return render_template("admins/add_translate.html")
