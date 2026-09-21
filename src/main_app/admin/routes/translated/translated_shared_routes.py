"""
Admin services and shared MethodViews for translated pages (``pages`` / ``pages_users`` tables).
"""

from __future__ import annotations

import logging

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from ....database.services import LangService, PagesService, UserPagesService

logger = logging.getLogger(__name__)


def _safe_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


class BaseTranslatedView(MethodView):
    """Base class for translated pages views supplying database services."""

    def __init__(
        self,
        service_name: str,
        endpoint_name: str,
        table_label: str,
    ) -> None:
        if service_name == "pages":
            self.service = PagesService()
        elif service_name == "pages_users":
            self.service = UserPagesService()
        else:
            raise ValueError(f"Unknown service_name: {service_name}")

        self.lang_service = LangService()
        self.endpoint_name = endpoint_name
        self.table_label = table_label


class TranslatedIndexView(BaseTranslatedView):
    """View to handle listing translated pages with pagination."""

    def get(self) -> str:
        """List translated pages with filter options."""
        lang = request.args.get("lang", "All")
        page = max(_safe_int(request.args.get("page"), 1), 1)
        limit = max(_safe_int(request.args.get("limit"), 500), 1)
        offset = (page - 1) * limit

        try:
            rows = self.service.list_translated(lang=lang, limit=limit, offset=offset)
            total_count = self.service.count_translated(lang=lang)
        except Exception:
            logger.exception("Failed to list translated pages lang=%r", lang)
            rows, total_count = [], 0

        langs = self.lang_service.list_langs()

        return render_template(
            "admins/translated/index.html",
            rows=rows,
            total_count=total_count,
            lang=lang,
            page=page,
            limit=limit,
            languages=langs,
            table_label=self.table_label,
            endpoint=f"adminpanel.{self.endpoint_name}.index",
            edit_endpoint=f"adminpanel.{self.endpoint_name}.edit",
            edit_post_endpoint=f"adminpanel.{self.endpoint_name}.edit",
        )


class TranslatedEditView(BaseTranslatedView):
    """View to handle rendering edit popup and processing page updates/deletions."""

    def get(self) -> str:
        """Render the edit popup form for a single page record."""
        page_id = _safe_int(request.args.get("id"), 0)
        if page_id <= 0:
            abort(400, description="id is required")

        row = self.service.get(page_id)
        if not row:
            abort(404)

        return render_template(
            "admins/translated/edit.html",
            row=row,
            post_endpoint=f"adminpanel.{self.endpoint_name}.edit",
        )

    def post(self) -> ResponseReturnValue:
        """Update or delete a page record from the popup form."""
        page_id = _safe_int(request.form.get("id"), 0)

        if page_id <= 0:
            flash("Invalid id supplied.", "danger")
            return redirect(url_for("adminpanel.edit_done"))

        if "delete" in request.form:
            return self._handle_delete(page_id)

        title = (request.form.get("title") or "").strip()
        target = (request.form.get("target") or "").strip()
        lang = (request.form.get("lang") or "").strip()
        user = (request.form.get("user") or "").strip()
        pupdate = (request.form.get("pupdate") or "").strip()

        if not title or not target or not lang or not user or not pupdate:
            flash("All fields (title, target, lang, user, pupdate) are required.", "danger")
            return redirect(url_for(f"adminpanel.{self.endpoint_name}.edit", id=page_id))

        try:
            self.service.update_page(
                page_id=page_id,
                title=title,
                target=target,
                lang=lang,
                user=user,
                pupdate=pupdate,
            )
            flash(f"{self.table_label} page id {page_id} updated.", "success")
        except Exception:
            logger.exception("Failed to update %s page id=%r", self.table_label, page_id)
            flash(f"Failed to update {self.table_label} page id {page_id}.", "danger")

        return redirect(url_for("adminpanel.edit_done"))

    def _handle_delete(self, page_id: int) -> ResponseReturnValue:
        """Process deletion of a page record."""
        deleted = self.service.delete(page_id)
        if deleted is False:
            flash(f"Failed to delete {self.table_label} page id {page_id}", "danger")
            logger.error("Failed to delete %s page id=%r", self.table_label, page_id)
        else:
            flash(f"{self.table_label} page id {page_id} deleted.", "success")

        return redirect(url_for("adminpanel.edit_done"))


class SharedTranslatedView:
    """Base routing registrar for translated page blueprints."""

    def __init__(self, service_name: str, endpoint_name: str, table_label: str) -> None:
        self.service_name = service_name
        self.endpoint_name = endpoint_name
        self.table_label = table_label

    def register(self, bp: Blueprint) -> None:
        """Register MethodViews for indexing and editing translated pages."""
        args = (self.service_name, self.endpoint_name, self.table_label)

        bp.add_url_rule("/", view_func=TranslatedIndexView.as_view("index", *args))
        bp.add_url_rule("/edit", view_func=TranslatedEditView.as_view("edit", *args))

        # Legacy endpoint mapping for backward compatibility
        bp.add_url_rule(
            "/edit",
            endpoint="edit_post",
            view_func=TranslatedEditView.as_view("legacy_edit_post", *args),
            methods=["POST"],
        )


__all__ = [
    "TranslatedIndexView",
    "TranslatedEditView",
    "SharedTranslatedView",
]
