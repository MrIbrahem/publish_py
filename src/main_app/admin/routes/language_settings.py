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

from ...db.services.config import LanguageSettingService
from ...db.services.content import list_langs
from ..decorators import admin_required

logger = logging.getLogger(__name__)


def _language_settings_dashboard():
    """Render the language settings management dashboard."""
    service = LanguageSettingService()
    settings = service.list_language_settings()
    # Also get all available languages for the "Add" dropdown
    languages = list_langs()

    return render_template(
        "admins/language_settings.html",
        settings=settings,
        languages=languages,
    )


def _add_language_setting() -> ResponseReturnValue:
    """Create a new language setting record."""

    lang_code = request.form.get("lang_code", "").strip()
    if not lang_code:
        flash("Language code is required.", "danger")
        return redirect(url_for("admin.language_settings.dashboard"))

    move_dots = 1 if request.form.get("move_dots") == "1" else 0
    expend = 1 if request.form.get("expend") == "1" else 0
    add_en_lang = 1 if request.form.get("add_en_lang") == "1" else 0

    try:
        service = LanguageSettingService()
        service.add_language_setting(
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

    return redirect(url_for("admin.language_settings.dashboard"))


def _update_language_setting(setting_id: int) -> ResponseReturnValue:
    """Update an existing language setting record."""

    # Using individual fields for update
    kwargs = {
        "move_dots": 1 if request.form.get("move_dots") == "1" else 0,
        "expend": 1 if request.form.get("expend") == "1" else 0,
        "add_en_lang": 1 if request.form.get("add_en_lang") == "1" else 0,
    }

    try:
        service = LanguageSettingService()
        record = service.update_language_setting(setting_id, **kwargs)
    except ValueError as exc:
        logger.exception("Unable to update language setting")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to update language setting.")
        flash("Unable to update language setting. Please try again.", "danger")
    else:
        flash(f"Language setting for '{record.lang_code}' updated.", "success")

    return redirect(url_for("admin.language_settings.dashboard"))


def _delete_language_setting(setting_id: int) -> ResponseReturnValue:
    """Remove a language setting record entirely."""

    try:
        service = LanguageSettingService()
        record = service.delete(setting_id)
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

    return redirect(url_for("admin.language_settings.dashboard"))


class LanguageSettings:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(admin_required(self.dashboard))
        self.bp.post("/add")(admin_required(self.add))
        self.bp.post("/<int:setting_id>/update")(admin_required(self.update))
        self.bp.post("/<int:setting_id>/delete")(admin_required(self.delete))

    def dashboard(self):
        return _language_settings_dashboard()

    def add(self) -> ResponseReturnValue:
        return _add_language_setting()

    def update(self, setting_id: int) -> ResponseReturnValue:
        return _update_language_setting(setting_id)

    def delete(self, setting_id: int) -> ResponseReturnValue:
        return _delete_language_setting(setting_id)


__all__ = [
    "LanguageSettings",
]
