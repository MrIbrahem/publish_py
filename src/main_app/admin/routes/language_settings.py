"""Admin-only routes for managing language-specific settings."""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue

from ...database.services import LangService, LanguageSettingService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


class LanguageSettings:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.service = LanguageSettingService()
        self.lang_service = LangService()
        self._setup_routes()

    def _setup_routes(self) -> None:

        routes = [
            ("/", "GET", self.dashboard),
            ("/add", "POST", self.add),
            ("/<int:setting_id>/update", "POST", self.update),
            ("/<int:setting_id>/delete", "POST", self.delete),
        ]
        for rule, method, target in routes:
            self.bp.route(rule, methods=[method])(admin_required(target))

    def dashboard(self):
        """Render the language settings management dashboard."""

        settings = self.service.list_language_settings()
        # Also get all available languages for the "Add" dropdown
        languages = self.lang_service.list_langs()

        return render_template(
            "admins/language_settings.html",
            settings=settings,
            languages=languages,
        )

    def add(self) -> ResponseReturnValue:
        """Create a new language setting record."""

        lang_code = request.form.get("lang_code", "").strip()
        if not lang_code:
            flash("Language code is required.", "danger")
            return redirect(url_for("adminpanel.language_settings.dashboard"))

        move_dots = 1 if request.form.get("move_dots") == "1" else 0
        expend = 1 if request.form.get("expend") == "1" else 0
        add_en_lang = 1 if request.form.get("add_en_lang") == "1" else 0

        try:

            self.service.add_language_setting(
                lang_code=lang_code,
                move_dots=move_dots,
                expend=expend,
                add_en_lang=add_en_lang,
            )
        except ValueError as exc:
            logger.exception("Unable to add language setting")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to add language setting.")
            flash("Unable to add language setting. Please try again.", "danger")
        else:
            flash(f"Language setting for '{lang_code}' added.", "success")

        return redirect(url_for("adminpanel.language_settings.dashboard"))

    def update(self, setting_id: int) -> ResponseReturnValue:
        """Update an existing language setting record."""
        # Using individual fields for update
        kwargs = {
            "move_dots": 1 if request.form.get("move_dots") == "1" else 0,
            "expend": 1 if request.form.get("expend") == "1" else 0,
            "add_en_lang": 1 if request.form.get("add_en_lang") == "1" else 0,
        }

        try:

            record = self.service.update_language_setting(setting_id, **kwargs)
        except ValueError as exc:
            logger.exception("Unable to update language setting")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to update language setting.")
            flash("Unable to update language setting. Please try again.", "danger")
        else:
            flash(f"Language setting for '{record.lang_code}' updated.", "success")

        return redirect(url_for("adminpanel.language_settings.dashboard"))

    def delete(self, setting_id: int) -> ResponseReturnValue:
        """Remove a language setting record entirely."""

        try:
            record = self.service.delete(setting_id)
            if not record:
                raise ValueError(f"Unable to delete setting with ID {setting_id}")
        except ValueError as exc:
            logger.exception("Unable to delete language setting")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to delete language setting.")
            flash("Unable to delete language setting. Please try again.", "danger")
        else:
            flash(f"Language setting for '{setting_id}' removed.", "success")

        return redirect(url_for("adminpanel.language_settings.dashboard"))


__all__ = [
    "LanguageSettings",
]
