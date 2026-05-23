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
    titles = request.form.getlist("mdtitle")
    cats = request.form.getlist("cat")
    types = request.form.getlist("type")
    users = request.form.getlist("user")
    langs = request.form.getlist("lang")
    targets = request.form.getlist("target")
    pupdates = request.form.getlist("pupdate")

    if not titles:
        flash("No translation data submitted.", "danger")
        return redirect(url_for("admin.add.add_translate"))

    texts: list[str] = []
    errors: list[str] = []

    for i in range(len(titles)):
        mdtitle = titles[i].strip()
        cat = cats[i].strip() if i < len(cats) else ""
        translate_type = types[i].strip() if i < len(types) else ""
        user = users[i].strip() if i < len(users) else ""
        lang = langs[i].strip() if i < len(langs) else ""
        target = targets[i].strip() if i < len(targets) else ""
        pupdate = pupdates[i].strip() if i < len(pupdates) else ""

        if not mdtitle or not lang or not user:
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
