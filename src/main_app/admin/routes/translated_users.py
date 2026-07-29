"""Admin routes for translated user pages (``pages_users`` table).

The 2 files following is the same, but:
- translated_users.py targets ``pages_users`` table.
- translated.py targets ``pages`` table.
"""

from __future__ import annotations

import logging

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from ...db.services import LangService, UserPagesService
from ...extensions import db

logger = logging.getLogger(__name__)


def _safe_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


class TranslatedUsersRoutes:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.service = UserPagesService()
        self.lang_service = LangService()
        self.endpoint_name = "translated_users"
        self.table_label = "User"
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(self.index)
        self.bp.route("/edit", methods=["GET"])(self.edit)
        self.bp.route("/edit", methods=["POST"])(self.edit_post)

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
            endpoint=f"admin.{self.endpoint_name}.index",
            edit_endpoint=f"admin.{self.endpoint_name}.edit",
            edit_post_endpoint=f"admin.{self.endpoint_name}.edit_post",
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
            post_endpoint=f"admin.{self.endpoint_name}.edit_post",
        )

    def edit_post(self) -> ResponseReturnValue:
        """Update or delete a single row from the popup form."""
        page_id = _safe_int(request.form.get("id"), 0)

        if page_id <= 0:
            flash("Invalid id supplied.", "danger")
            return redirect(url_for("admin.edit_done"))

        if "delete" in request.form:
            try:
                self.service.delete(page_id)
                flash(f"{self.table_label} page id {page_id} deleted.", "success")
            except Exception:
                logger.exception(f"Failed to delete {self.table_label} page id=%r", page_id)
                flash(f"Failed to delete {self.table_label} page id {page_id}.", "danger")
            return redirect(url_for("admin.edit_done"))

        title = (request.form.get("title") or "").strip()
        target = (request.form.get("target") or "").strip()
        lang = (request.form.get("lang") or "").strip()
        user = (request.form.get("user") or "").strip()
        pupdate = (request.form.get("pupdate") or "").strip()

        if not title or not target or not lang or not user or not pupdate:
            flash("All fields (title, target, lang, user, pupdate) are required.", "danger")
            return redirect(url_for(f"admin.{self.endpoint_name}.edit", id=page_id))

        try:
            row = self.service.update_page(
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
            flash(f"{self.table_label} page id {page_id} updated.", "success")
        except Exception:
            logger.exception(f"Failed to update {self.table_label} page id=%r", page_id)
            flash(f"Failed to update {self.table_label} page id {page_id}.", "danger")

        return redirect(url_for("admin.edit_done"))


__all__ = [
    "TranslatedUsersRoutes",
]
