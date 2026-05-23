"""Admin route for Translations add_translate dashboard."""

from __future__ import annotations

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from ...db.services.content.category_service import list_categories
from ...db.services.pages.page_service import add_translate_row_to_db

logger = logging.getLogger(__name__)


add_bp = Blueprint("add", __name__, url_prefix="/add")


@add_bp.route("/", methods=["GET"])
def add_translate() -> str:
    """Render the translations add_translate dashboard."""
    categories = list_categories()
    return render_template("admins/add_translate.html", categories=categories)


@add_bp.route("/", methods=["POST"])
def add_translate_post() -> ResponseReturnValue:
    """Process the add_translate form submission."""
    form_data = request.form.to_dict(flat=False)
    rows = form_data.get("rows", {})

    if not rows:
        flash("No translation data submitted.", "danger")
        logger.warning("form_data")
        logger.warning(form_data)
        return redirect(url_for("admin.add.add_translate"))

    texts: list[str] = []
    errors: list[str] = []

    for _idx, row in rows.items():
        mdtitle = (row.get("mdtitle") or "").strip()
        if isinstance(mdtitle, list):
            mdtitle = mdtitle[0] if mdtitle else ""
        cat = (row.get("cat") or "").strip()
        if isinstance(cat, list):
            cat = cat[0] if cat else ""
        translate_type = (row.get("type") or "").strip()
        if isinstance(translate_type, list):
            translate_type = translate_type[0] if translate_type else ""
        user = (row.get("user") or "").strip()
        if isinstance(user, list):
            user = user[0] if user else ""
        lang = (row.get("lang") or "").strip()
        if isinstance(lang, list):
            lang = lang[0] if lang else ""
        target = (row.get("target") or "").strip()
        if isinstance(target, list):
            target = target[0] if target else ""
        pupdate = (row.get("pupdate") or "").strip()
        if isinstance(pupdate, list):
            pupdate = pupdate[0] if pupdate else ""

        if not mdtitle or not lang or not user:
            errors.append("Failed to add translations. Missing required fields.")
            continue

        try:
            result = add_translate_row_to_db(
                title=mdtitle,
                translate_type=translate_type,
                cat=cat,
                lang=lang,
                user=user,
                target=target,
                pupdate=pupdate,
            )
        except Exception:
            logger.exception("Failed to add translation for title=%r", mdtitle)
            result = False

        if result:
            texts.append("Translations added successfully.")
        else:
            errors.append("Failed to add translations.")

    for t in texts:
        flash(t, "success")
    for e in errors:
        flash(e, "danger")

    return redirect(url_for("admin.add.add_translate"))
