"""Admin route for Translations add_translate dashboard."""

from __future__ import annotations

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from ...database.services import CategoryService, PagesService

logger = logging.getLogger(__name__)


class AddTranslateView(MethodView):
    """View for displaying and processing the translation addition dashboard."""

    def __init__(self) -> None:
        self.category_service = CategoryService()
        self.pages_service = PagesService()

    def get(self) -> str:
        """Render the translations add_translate dashboard."""
        categories = self.category_service.list_categories()
        return render_template(
            "admins/add_translate.html",
            categories=categories,
        )

    def post(self) -> ResponseReturnValue:
        """Process the add_translate form submission."""
        titles = request.form.getlist("mdtitle")
        cats = request.form.getlist("cat")
        types = request.form.getlist("tra_type")
        users = request.form.getlist("user")
        langs = request.form.getlist("lang")
        targets = request.form.getlist("target")
        pupdates = request.form.getlist("pupdate")

        if not titles:
            flash("No translation data submitted.", "danger")
            return redirect(url_for("adminpanel.add.add_translate"))

        texts: list[str] = []
        errors: list[str] = []

        def get_val(lst: list[str], idx: int) -> str:
            return lst[idx].strip() if idx < len(lst) else ""

        for i, title in enumerate(titles):
            mdtitle = title.strip()
            cat = get_val(cats, i)
            translate_type = get_val(types, i)
            user = get_val(users, i)
            lang = get_val(langs, i)
            target = get_val(targets, i)
            pupdate = get_val(pupdates, i)

            if not mdtitle or not lang or not user:
                continue

            try:
                result = self.pages_service.add_translate_row_to_db(
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

        return redirect(url_for("adminpanel.add.add_translate"))

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register view routes directly on the blueprint."""
        bp.add_url_rule("/", view_func=cls.as_view("add_translate"))


class AddTranslateRoutes:
    """Registrar class for AddTranslate views."""

    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.add_url_rule(
            "/",
            view_func=AddTranslateView.as_view("add_translate"),
        )


__all__ = [
    "AddTranslateView",
    "AddTranslateRoutes",
]
