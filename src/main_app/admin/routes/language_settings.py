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
from flask.views import MethodView

from ...database.services import LangService, LanguageSettingService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


class BaseLanguageSettingsView(MethodView):
    """Base view for the language-settings pages.

    Holds the services shared by every language-settings page. All
    language-settings pages require an administrator.
    """

    decorators = [admin_required]

    def __init__(self) -> None:
        self.service = LanguageSettingService()
        self.lang_service = LangService()


class LanguageSettingsDashboardView(BaseLanguageSettingsView):
    """Render the language settings management dashboard."""

    def get(self) -> str:
        """Render the settings table plus the language dropdown."""
        settings = self.service.list_language_settings()
        # Also get all available languages for the "Add" dropdown
        languages = self.lang_service.list_langs()

        return render_template(
            "admins/language_settings.html",
            settings=settings,
            languages=languages,
        )


class LanguageSettingsAddView(BaseLanguageSettingsView):
    """Create a new language setting record."""

    def post(self) -> ResponseReturnValue:
        """Validate the language code and create the setting."""

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


class LanguageSettingsUpdateView(BaseLanguageSettingsView):
    """Update an existing language setting record."""

    def post(self, setting_id: int) -> ResponseReturnValue:
        """Apply the submitted flags to the setting ``setting_id``."""
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


class LanguageSettingsDeleteView(BaseLanguageSettingsView):
    """Remove a language setting record entirely."""

    def post(self, setting_id: int) -> ResponseReturnValue:
        """Delete the setting identified by ``setting_id``."""

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


class LanguageSettings:
    """Registrar wiring the language-settings MethodViews onto a blueprint.

    Endpoint names (``dashboard``, ``add``, ``update``, ``delete``) are
    preserved from the legacy function-based routes so existing
    ``url_for('adminpanel.language_settings.add')`` calls keep working.
    """

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the dashboard and the setting write endpoints."""
        bp.add_url_rule("/", view_func=LanguageSettingsDashboardView.as_view("dashboard"), methods=["GET"])
        bp.add_url_rule("/add", view_func=LanguageSettingsAddView.as_view("add"), methods=["POST"])
        bp.add_url_rule(
            "/<int:setting_id>/update", view_func=LanguageSettingsUpdateView.as_view("update"), methods=["POST"]
        )
        bp.add_url_rule(
            "/<int:setting_id>/delete", view_func=LanguageSettingsDeleteView.as_view("delete"), methods=["POST"]
        )


__all__ = [
    "LanguageSettings",
]
