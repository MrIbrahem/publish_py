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

from ...db.services.content import list_categories
from ...db.services.pages import translate_type_service
from ...shared.core.extensions import UniqueError

logger = logging.getLogger(__name__)

tt_bp = Blueprint("tt", __name__, url_prefix="/tt")


@tt_bp.route("/", methods=["GET"])
def tt_index() -> str:
    """Render the Translate Type listing."""
    cat = request.args.get("cat", "All")
    translate_types = []
    new_titles = []
    try:
        translate_types = translate_type_service.list_translate_types(cat=cat)
        # new_titles = translate_type_service.list_new_titles() if cat == "All" else []
    except Exception:
        logger.exception("Failed to load translate_type rows for cat=%r", cat)

    categories = list_categories()
    return render_template(
        "admins/tt/index.html",
        translate_types=translate_types,
        # new_titles=new_titles,
        categories=categories,
        cat=cat,
    )


@tt_bp.route("/edit", methods=["GET"])
def tt_edit() -> str:
    """Render the add/edit popup form for a single translate_type row."""
    tt_id_raw = request.args.get("id", "")
    if not tt_id_raw:
        flash("Invalid id.", "danger")
        return redirect(url_for("admin.edit_done"))
    try:
        tt_id = int(tt_id_raw)
        translate_types = translate_type_service.get_translate_type(tt_id)
    except (ValueError, TypeError):
        logger.exception("Invalid translate_type id=%r", tt_id_raw)
        translate_types = None

    if not translate_types:
        flash(f"Failed to load translate_type id={tt_id}", "danger")
        return redirect(url_for("admin.edit_done"))

    return render_template(
        "admins/tt/edit.html",
        post_endpoint="admin.tt.tt_edit_post",
        id=translate_types.tt_id,
        title=translate_types.tt_title,
        lead=translate_types.tt_lead,
        full=translate_types.tt_full,
    )


@tt_bp.route("/", methods=["POST"])
def tt_edit_post() -> ResponseReturnValue:
    """Insert or update a translate_type row from the popup form."""
    tt_id_raw = (request.form.get("id") or "").strip()
    title = (request.form.get("title") or "").strip()
    lead = 1 if request.form.get("lead") == "1" else 0
    full = 1 if request.form.get("full") == "1" else 0

    if not title:
        flash("Title is required.", "danger")
        return redirect(url_for("admin.tt.tt_edit", id=tt_id_raw))

    tt_id: int | None = None
    if tt_id_raw:
        try:
            tt_id = int(tt_id_raw)
        except ValueError:
            flash(f"Invalid id: {tt_id_raw}", "danger")
            return redirect(url_for("admin.tt.tt_edit", id=tt_id_raw))

    try:
        translate_types = translate_type_service.get_translate_type(tt_id)
    except Exception:
        logger.exception("Failed to load translate_type rows for id=%r", tt_id)
        translate_types = None

    if not translate_types:
        flash(f"Failed to load translate_type id={tt_id}", "danger")
        return redirect(url_for("admin.edit_done"))

    try:
        result = translate_type_service.update_translate_type(tt_id, title, lead, full)
    except UniqueError:
        logger.warning("Failed to update translate_type, duplicate item with title=%r", title)
        flash(f"Failed, title: {title} is used in other item.", "danger")
        return redirect(url_for("admin.tt.tt_edit", id=tt_id_raw))

    except Exception:
        logger.exception("Failed to upsert translate_type id=%r title=%r", tt_id, title)
        result = False

    if result:
        flash(f"Translate type saved successfully, title: {title}.", "success")
        return redirect(url_for("admin.edit_done"))

    flash(f"Failed to save translate type, title: {title}.", "danger")
    return redirect(url_for("admin.tt.tt_edit", id=tt_id_raw))


@tt_bp.route("/add", methods=["GET"])
def add() -> str:
    return render_template(
        "admins/tt/edit.html",
        post_endpoint="admin.tt.tt_add_post",
        id="",
        title="",
        lead=1,
        full=0,
        new=1,
    )


@tt_bp.route("/add", methods=["POST"])
def tt_add_post() -> ResponseReturnValue:
    """Insert a translate_type row from the popup form."""
    title = (request.form.get("title") or "").strip()
    lead = 1 if request.form.get("lead") == "1" else 0
    full = 1 if request.form.get("full") == "1" else 0

    if not title:
        flash("Title is required.", "danger")
        return redirect(url_for("admin.tt.add"))

    try:
        result = translate_type_service.add_translate_type(tt_title=title, tt_lead=lead, tt_full=full)
    except UniqueError:
        logger.warning("Failed to insert translate_type, duplicate item with title=%r", title)
        flash(f"Failed, title: {title} is used in other item.", "danger")
        return redirect(url_for("admin.tt.add"))
    except Exception:
        logger.exception("Failed to insert translate_type title=%r", title)
        result = False

    if result:
        flash(f"Translate type saved successfully, title: {title}.", "success")
        return redirect(url_for("admin.edit_done"))

    flash(f"Failed to save translate type, title: {title}.", "danger")
    return redirect(url_for("admin.tt.add"))
