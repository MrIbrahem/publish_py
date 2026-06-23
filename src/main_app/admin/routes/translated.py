"""Admin routes for translated main pages (``pages`` table).

Mirrors the PHP under ``coordinator/admin/translated/*.php`` for ``table=pages``:
- ``index.php`` -> ``GET /``
- ``edit_page.php`` GET -> ``GET /edit``
- ``edit_page.php`` POST -> ``POST /edit``
"""

from __future__ import annotations

import logging

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from ...db.services.content import list_langs
from ...db.services.pages import (
    count_translated,
    delete_page,
    get_page_by_id,
    list_translated,
    update_page,
)
from ...shared.core.extensions import db

logger = logging.getLogger(__name__)


translated_bp = Blueprint("translated", __name__, url_prefix="/translated")


def _safe_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


@translated_bp.route("/", methods=["GET"])
def index() -> str:
    """List translated main pages with pagination."""
    lang = request.args.get("lang", "All")
    page = max(_safe_int(request.args.get("page"), 1), 1)
    limit = max(_safe_int(request.args.get("limit"), 500), 1)
    offset = (page - 1) * limit

    try:
        rows = list_translated(lang=lang, limit=limit, offset=offset)
        total_count = count_translated(lang=lang)
    except Exception:
        logger.exception("Failed to list translated pages lang=%r", lang)
        rows, total_count = [], 0

    return render_template(
        "admins/translated/index.html",
        rows=rows,
        total_count=total_count,
        lang=lang,
        page=page,
        limit=limit,
        languages=list_langs(),
        table_label="Main",
        endpoint="admin.translated.index",
        edit_endpoint="admin.translated.edit",
        edit_post_endpoint="admin.translated.edit_post",
    )


@translated_bp.route("/edit", methods=["GET"])
def edit() -> str:
    """Render the edit popup for a single ``pages`` row."""
    page_id = _safe_int(request.args.get("id"), 0)
    if page_id <= 0:
        abort(400, description="id is required")

    row = get_page_by_id(page_id)
    if not row:
        abort(404)

    return render_template(
        "admins/translated/edit.html",
        row=row,
        post_endpoint="admin.translated.edit_post",
    )


@translated_bp.route("/edit", methods=["POST"])
def edit_post() -> ResponseReturnValue:
    """Update or delete a single ``pages`` row from the popup form."""
    page_id = _safe_int(request.form.get("id"), 0)

    if page_id <= 0:
        flash("Invalid id supplied.", "danger")
        return redirect(url_for("admin.edit_done"))

    if "delete" in request.form:
        try:
            delete_page(page_id)
            flash(f"Page id {page_id} deleted.", "success")
        except Exception:
            logger.exception("Failed to delete page id=%r", page_id)
            flash(f"Failed to delete page id {page_id}.", "danger")
        return redirect(url_for("admin.edit_done"))

    title = (request.form.get("title") or "").strip()
    target = (request.form.get("target") or "").strip()
    lang = (request.form.get("lang") or "").strip()
    user = (request.form.get("user") or "").strip()
    pupdate = (request.form.get("pupdate") or "").strip()

    if not title or not target or not lang or not user or not pupdate:
        flash("All fields (title, target, lang, user, pupdate) are required.", "danger")
        return redirect(url_for("admin.translated.edit", id=page_id))

    try:
        row = update_page(
            page_id=page_id,
            title=title,
            target=target,
            lang=lang,
            user=user,
        )
        # pupdate is a separate column not handled by update_page's positional args
        if row is not None:
            row.pupdate = pupdate
            db.session.commit()
        flash(f"Page id {page_id} updated.", "success")
    except Exception:
        logger.exception("Failed to update page id=%r", page_id)
        flash(f"Failed to update page id {page_id}.", "danger")

    return redirect(url_for("admin.edit_done"))
