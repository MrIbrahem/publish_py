"""
Admin shared routes for translated pages from (``pages``/``pages_users`` table).
"""

from __future__ import annotations

import logging

from flask import abort, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from ....db.services import LangService, PagesService, UserPagesService

logger = logging.getLogger(__name__)


def _safe_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


class SharedTranslatedRoutes:
    """
    Generic service class for pages_users/pages routes.

    usage, e.g.::
        class TranslatedUsersRoutes(SharedTranslatedRoutes):
            def __init__(self, bp: Blueprint) -> None:
                self.bp = bp
                super().__init__(
                    service_name="pages_users",
                    endpoint_name="translated_users",
                    table_label="User",
                )
                self._setup_routes()

        class TranslatedRoutes(SharedTranslatedRoutes):
            def __init__(self, bp: Blueprint) -> None:
                self.bp = bp
                super().__init__(
                    service_name="pages",
                    endpoint_name="translated",
                    table_label="Main",
                )
                self._setup_routes()

    """

    def __init__(self, service_name: str, endpoint_name: str, table_label: str) -> None:
        if service_name == "pages":
            self.service = PagesService()
        elif service_name == "pages_users":
            self.service = UserPagesService()

        self.lang_service = LangService()
        self.endpoint_name = endpoint_name
        self.table_label = table_label

    def index(self) -> str:
        """List translated pages with pagination."""
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
            edit_post_endpoint=f"adminpanel.{self.endpoint_name}.edit_post",
        )

    def edit(self) -> str:
        """Render the edit popup for a single row."""
        page_id = _safe_int(request.args.get("id"), 0)
        if page_id <= 0:
            abort(400, description="id is required")

        row = self.service.get(page_id)
        if not row:
            abort(404)

        return render_template(
            "admins/translated/edit.html",
            row=row,
            post_endpoint=f"adminpanel.{self.endpoint_name}.edit_post",
        )

    def edit_post(self) -> ResponseReturnValue:
        """Update or delete a single row from the popup form."""
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
            logger.exception(f"Failed to update {self.table_label} page id=%r", page_id)
            flash(f"Failed to update {self.table_label} page id {page_id}.", "danger")

        return redirect(url_for("adminpanel.edit_done"))

    def _handle_delete(self, page_id: int) -> ResponseReturnValue:

        deleted = self.service.delete(page_id)
        if deleted is False:
            flash(f"Failed to delete {self.table_label} page id {page_id}")
            logger.error(f"Failed to delete {self.table_label} page id=%r", page_id)
        else:
            flash(f"{self.table_label} page id {page_id} deleted.", "success")

        return redirect(url_for("adminpanel.edit_done"))


__all__ = [
    "SharedTranslatedRoutes",
]
