"""Admin routes for the Translate Type (``tt``) blueprint.

Mirrors the PHP code under ``coordinator/admin/tt/*.php``:
- ``index.php`` -> ``GET /``
- ``edit_translate_type.php`` -> ``GET /edit``
- ``post.php`` -> ``POST /``
"""

from __future__ import annotations

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from ...db.services.content.category_service import list_categories
from ...db.services.pages import translate_type_service

logger = logging.getLogger(__name__)


tt_bp = Blueprint("tt", __name__, url_prefix="/tt")


@tt_bp.route("/", methods=["GET"])
def tt_index() -> str:
    """Render the Translate Type listing."""
    cat = request.args.get("cat", "All")
    try:
        translate_types = translate_type_service.list_translate_types(cat=cat)
        new_titles = translate_type_service.list_new_titles() if cat == "All" else []
    except Exception:
        logger.exception("Failed to load translate_type rows for cat=%r", cat)
        translate_types = []
        new_titles = []

    categories = list_categories()
    return render_template(
        "admins/tt.html",
        translate_types=translate_types,
        new_titles=new_titles,
        categories=categories,
        cat=cat,
    )


@tt_bp.route("/edit", methods=["GET"])
def tt_edit() -> str:
    """Render the add/edit popup form for a single translate_type row."""
    return render_template(
        "admins/tt_edit.html",
        id=request.args.get("id", ""),
        title=request.args.get("title", ""),
        lead=request.args.get("lead", ""),
        full=request.args.get("full", ""),
    )


@tt_bp.route("/", methods=["POST"])
def tt_post() -> ResponseReturnValue:
    """Insert or update a translate_type row from the popup form."""
    tt_id_raw = (request.form.get("id") or "").strip()
    title = (request.form.get("title") or "").strip()
    lead = 1 if request.form.get("lead") == "1" else 0
    full = 1 if request.form.get("full") == "1" else 0

    if not title:
        flash("Title is required.", "danger")
        return redirect(url_for("admin.tt.tt_index"))

    tt_id: int | None = None
    if tt_id_raw:
        try:
            tt_id = int(tt_id_raw)
        except ValueError:
            flash(f"Invalid id: {tt_id_raw}", "danger")
            return redirect(url_for("admin.tt.tt_index"))

    try:
        result = translate_type_service.upsert(tt_id, title, lead, full)
    except Exception:
        logger.exception("Failed to upsert translate_type id=%r title=%r", tt_id, title)
        result = False

    if result:
        flash(f"Translate type saved successfully, title: {title}.", "success")
    else:
        flash(f"Failed to save translate type, title: {title}.", "danger")

    return redirect(url_for("admin.tt.tt_index"))
