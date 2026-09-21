"""Admin routes for moving user pages to main pages.

Mirrors PHP under ``coordinator/admin/pages_users_to_main/*.php``.
"""

from __future__ import annotations

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from ...database.services import LangService, PagesService, PagesUsersToMainPagesService

logger = logging.getLogger(__name__)


def _safe_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


class BasePagesUsersMainView(MethodView):
    """Base view for the pages-users-to-main pages.

    Holds the services shared by every page of this feature. Note that
    these endpoints are intentionally left unguarded to match the
    legacy behavior.
    """

    def __init__(self) -> None:
        self.pum_service = PagesUsersToMainPagesService()
        self.lang_service = LangService()
        self.pages_service = PagesService()


class PagesUsersToMainIndexView(BasePagesUsersMainView):
    """List the user pages flagged for promotion to main pages."""

    def get(self) -> str:
        """Render the pending promotions table for a language."""
        lang = request.args.get("lang", "All")

        try:
            rows = self.pum_service.list_pending(lang=lang)
        except Exception:
            logger.exception("Failed to list pages_users_to_main lang=%r", lang)
            rows = []

        return render_template(
            "admins/pages_users_to_main.html",
            rows=rows,
            lang=lang,
            languages=self.lang_service.list_langs(),
        )


class PagesUsersToMainFixItView(BasePagesUsersMainView):
    """Render the fix_it form used to promote a single user page."""

    def get(self) -> str:
        """Render the promotion form for the page identified by ``id``."""
        page_id = _safe_int(request.args.get("id"), 0)
        new_user = (request.args.get("new_user") or "").strip()
        new_target = (request.args.get("new_target") or "").strip()

        user_page = self.pum_service.get_user_page(page_id) if page_id > 0 else None
        title = user_page.title if user_page else ""
        lang = user_page.lang if user_page else ""
        old_target = user_page.target if user_page else ""
        pupdate = user_page.pupdate if user_page else ""

        duplicate_page = None
        if title and lang:
            duplicate_page = self.pum_service.check_main_page_exists(title, lang)

        return render_template(
            "admins/pages_users_to_main_fix_it.html",
            id=page_id,
            title=title,
            lang=lang,
            old_target=old_target,
            new_user=new_user,
            new_target=new_target,
            pupdate=pupdate,
            duplicate_page=duplicate_page,
        )


class PagesUsersToMainFixItPostView(BasePagesUsersMainView):
    """Promote a user page to main and remove the source rows."""

    def post(self) -> ResponseReturnValue:
        """Promote a user page to main and delete the source rows."""
        page_id = _safe_int(request.form.get("id"), 0)
        title = (request.form.get("title") or "").strip()
        lang = (request.form.get("lang") or "").strip()
        new_target = (request.form.get("new_target") or "").strip()
        new_user = (request.form.get("new_user") or "").strip()
        pupdate = (request.form.get("pupdate") or "").strip()

        redirect_to = redirect(url_for("adminpanel.pages_users_to_main.pages_users_to_main_index"))

        if page_id <= 0:
            flash("Invalid id supplied.", "danger")
            return redirect_to

        if not title or not lang or not new_target or not new_user or not pupdate:
            flash("All fields (title, lang, new_target, new_user, pupdate) are required.", "danger")
            return redirect_to

        user_page = self.pum_service.get_user_page(page_id)
        if not user_page:
            flash(f"Page with id:({page_id}) not found.", "danger")
            return redirect_to

        translate_type = user_page.translate_type or ""
        cat = user_page.cat or ""
        word = user_page.word or 0

        try:
            added = self.pages_service.add_translate_row_to_db(
                title=title,
                translate_type=translate_type,
                cat=cat,
                lang=lang,
                user=new_user,
                target=new_target,
                pupdate=pupdate,
                word=word,
            )
        except Exception:
            logger.exception("add_translate_row_to_db failed for id=%r", page_id)
            added = False

        if not added:
            flash("Failed to add translations.", "danger")
            return redirect_to

        # ``add_translate_row_to_db`` only commits on the INSERT branch; when it
        # updates an existing row the change stays pending in the session. If the
        # later ``delete_user_page`` call rolls the session back, that pending
        # update would silently disappear even though we just flashed success.
        # Force the commit here so the flash matches what is actually persisted.
        try:
            self.pages_service.commit_pending_updates()
        except Exception:
            logger.exception("Failed to commit add_translate_row_to_db for id=%r", page_id)
            flash("Failed to persist translations.", "danger")
            return redirect_to

        flash("Translations added successfully.", "success")

        try:
            deleted = self.pum_service.delete_user_page_to_main(page_id)
        except Exception:
            logger.exception("delete_user_page failed for id=%r", page_id)
            deleted = False

        if deleted:
            flash(f"Page with id:({page_id}) deleted from pages_users.", "success")
        else:
            flash(f"Failed to delete page with id:({page_id}).", "danger")

        return redirect_to


__all__ = [
    "PagesUsersMainRoutes",
]
