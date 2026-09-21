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
from flask.views import MethodView
from werkzeug.wrappers.response import Response

from ...database.services import CategoryService, TranslateTypeService
from ...extensions import UniqueError

logger = logging.getLogger(__name__)


class BaseTranslateTypeView(MethodView):
    """Base view for the Translate Type pages.

    Holds the services shared by every translate-type page.
    """

    def __init__(self) -> None:
        self.translate_type_service = TranslateTypeService()
        self.category_service = CategoryService()


class TTIndexView(BaseTranslateTypeView):
    """Render the Translate Type listing."""

    def get(self) -> str:
        """Render the translate-type table for a category."""
        cat = request.args.get("cat", "All")
        translate_types = []
        try:
            translate_types = self.translate_type_service.list_translate_types(cat=cat)
            # new_titles = self.translate_type_service.list_new_titles() if cat == "All" else []
        except Exception:
            logger.exception("Failed to load translate_type rows for cat=%r", cat)

        categories = self.category_service.list_categories()

        return render_template(
            "admins/tt/index.html",
            translate_types=translate_types,
            # new_titles=new_titles,
            categories=categories,
            cat=cat,
        )


class TTEditView(BaseTranslateTypeView):
    """Render the add/edit popup form for a single translate_type row."""

    def get(self) -> Response | str:
        """Render the edit form for the row identified by ``id``."""
        tt_id_raw = request.args.get("id", "")
        if not tt_id_raw:
            flash("Invalid id.", "danger")
            return redirect(url_for("adminpanel.edit_done"))
        try:
            tt_id = int(tt_id_raw)
            translate_types = self.translate_type_service.get_translate_type(tt_id)
        except (ValueError, TypeError):
            logger.exception("Invalid translate_type id=%r", tt_id_raw)
            translate_types = None

        if not translate_types:
            flash(f"Failed to load translate_type tt_id_raw={tt_id_raw}", "danger")
            return redirect(url_for("adminpanel.edit_done"))

        return render_template(
            "admins/tt/edit.html",
            post_endpoint="adminpanel.tt.tt_edit_post",
            id=translate_types.tt_id,
            title=translate_types.tt_title,
            lead=translate_types.tt_lead,
            full=translate_types.tt_full,
        )


class TTEditPostView(BaseTranslateTypeView):
    """Insert or update a translate_type row from the popup form."""

    def post(self) -> ResponseReturnValue:
        """Validate the submitted form and update the matching row."""
        tt_id_raw = (request.form.get("id") or "").strip()
        title = (request.form.get("title") or "").strip()
        lead = 1 if request.form.get("lead") == "1" else 0
        full = 1 if request.form.get("full") == "1" else 0

        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("adminpanel.tt.tt_edit", id=tt_id_raw))

        tt_id: int | None = None
        if tt_id_raw:
            try:
                tt_id = int(tt_id_raw)
            except ValueError:
                flash(f"Invalid id: {tt_id_raw}", "danger")
                return redirect(url_for("adminpanel.tt.tt_edit", id=tt_id_raw))

        if not tt_id:
            flash(f"Failed to load translate_type id={tt_id}", "danger")
            return redirect(url_for("adminpanel.edit_done"))

        try:
            translate_types = self.translate_type_service.get_translate_type(tt_id)
        except Exception:
            logger.exception("Failed to load translate_type rows for id=%r", tt_id)
            translate_types = None

        if not translate_types:
            flash(f"Failed to load translate_type id={tt_id}", "danger")
            return redirect(url_for("adminpanel.edit_done"))

        try:
            result = self.translate_type_service.update_translate_type(tt_id, title, lead, full)
        except UniqueError:
            logger.warning("Failed to update translate_type, duplicate item with title=%r", title)
            flash(f"Failed, title: {title} is used in other item.", "danger")
            return redirect(url_for("adminpanel.tt.tt_edit", id=tt_id_raw))

        except Exception:
            logger.exception("Failed to upsert translate_type id=%r title=%r", tt_id, title)
            result = False

        if result:
            flash(f"Translate type saved successfully, title: {title}.", "success")
            return redirect(url_for("adminpanel.edit_done"))

        flash(f"Failed to save translate type, title: {title}.", "danger")
        return redirect(url_for("adminpanel.tt.tt_edit", id=tt_id_raw))


class TTAddView(BaseTranslateTypeView):
    """Render the "add translate type" popup form."""

    def get(self) -> str:
        """Render the empty edit form configured for creation."""
        return render_template(
            "admins/tt/edit.html",
            post_endpoint="adminpanel.tt.tt_add_post",
            id="",
            title="",
            lead=1,
            full=0,
            new=1,
        )


class TTAddPostView(BaseTranslateTypeView):
    """Insert a translate_type row from the popup form."""

    def post(self) -> ResponseReturnValue:
        """Validate the submitted form and insert a new row."""
        title = (request.form.get("title") or "").strip()
        lead = 1 if request.form.get("lead") == "1" else 0
        full = 1 if request.form.get("full") == "1" else 0

        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("adminpanel.tt.add"))

        try:
            result = self.translate_type_service.add_translate_type(tt_title=title, tt_lead=lead, tt_full=full)
        except UniqueError:
            logger.warning("Failed to insert translate_type, duplicate item with title=%r", title)
            flash(f"Failed, title: {title} is used in other item.", "danger")
            return redirect(url_for("adminpanel.tt.add"))
        except Exception:
            logger.exception("Failed to insert translate_type title=%r", title)
            result = False

        if result:
            flash(f"Translate type saved successfully, title: {title}.", "success")
            return redirect(url_for("adminpanel.edit_done"))

        flash(f"Failed to save translate type, title: {title}.", "danger")
        return redirect(url_for("adminpanel.tt.add"))


class TranslateTypeRoutes:
    """Registrar wiring the translate-type MethodViews onto a blueprint.

    Endpoint names (``tt_index``, ``tt_edit``, ``tt_edit_post``, ``add``,
    ``tt_add_post``) are preserved from the legacy function-based routes
    so existing ``url_for('adminpanel.tt.tt_edit_post')`` calls keep
    working.
    """

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the listing, edit and add endpoints."""
        bp.add_url_rule("/", view_func=TTIndexView.as_view("tt_index"), methods=["GET"])
        bp.add_url_rule("/edit", view_func=TTEditView.as_view("tt_edit"), methods=["GET"])
        bp.add_url_rule("/", view_func=TTEditPostView.as_view("tt_edit_post"), methods=["POST"])
        bp.add_url_rule("/add", view_func=TTAddView.as_view("add"), methods=["GET"])
        bp.add_url_rule("/add", view_func=TTAddPostView.as_view("tt_add_post"), methods=["POST"])


__all__ = [
    "TranslateTypeRoutes",
]
