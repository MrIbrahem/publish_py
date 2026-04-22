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

from ...shared.services.lang_service import list_langs
from ...shared.services.language_setting_service import (
    add_language_setting,
    delete_language_setting,
    list_language_settings,
    update_language_setting,
)
from ..decorators import admin_required

logger = logging.getLogger(__name__)


def _language_settings_dashboard():
    """Render the language settings management dashboard."""

    settings = list_language_settings()
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
        add_language_setting(
            lang_code=lang_code,
            move_dots=move_dots,
            expend=expend,
            add_en_lang=add_en_lang,
        )
    except ValueError as exc:
        logger.warning(f"Unable to add language setting: {exc}")
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
        record = update_language_setting(setting_id, **kwargs)
    except ValueError as exc:
        logger.warning(f"Unable to update language setting: {exc}")
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
        record = delete_language_setting(setting_id)
    except ValueError as exc:
        logger.warning(f"Unable to delete language setting: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to delete language setting.")
        flash("Unable to delete language setting. Please try again.", "danger")
    else:
        flash(f"Language setting for '{record.lang_code}' removed.", "success")

    return redirect(url_for("admin.language_settings.dashboard"))


class LanguageSettings:
    def __init__(self):
        self.bp = Blueprint("language_settings", __name__, url_prefix="/language_settings")
        self._setup_routes()

    def _setup_routes(self):

        @self.bp.get("/")
        @admin_required
        def dashboard():
            return _language_settings_dashboard()

        @self.bp.post("/add")
        @admin_required
        def add() -> ResponseReturnValue:
            return _add_language_setting()

        @self.bp.post("/<int:setting_id>/update")
        @admin_required
        def update(setting_id: int) -> ResponseReturnValue:
            return _update_language_setting(setting_id)

        @self.bp.post("/<int:setting_id>/delete")
        @admin_required
        def delete(setting_id: int) -> ResponseReturnValue:
            return _delete_language_setting(setting_id)


languagesettings_module = LanguageSettings()
