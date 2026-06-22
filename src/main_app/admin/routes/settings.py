"""Admin-only routes for managing application settings."""

from __future__ import annotations

import json
import re
from typing import Any

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ...db.services.config import setting_service as service
from ..decorators import admin_required


def settings_update_form(request_form) -> tuple[list[str], list[str]]:
    all_settings = service.list_settings()
    failed_keys: list[str] = []
    deleted_keys: list[str] = []

    for setting in all_settings:
        key = setting.key
        v_type = setting.value_type
        form_key = f"setting_{key}"
        delete_key = f"delete_{key}"

        # Check if marked for deletion
        if request_form.get(delete_key) == "on":
            try:
                service.delete_setting(setting.id)
                deleted_keys.append(key)
            except Exception:
                failed_keys.append(key)
            continue

        if v_type == "boolean":
            raw_val = request_form.get(form_key, "")
        elif form_key in request_form:
            raw_val = request_form.get(form_key, "")
        else:
            continue

        value, success = _parse_setting_value(v_type, raw_val)
        if not success:
            failed_keys.append(key)
            continue

        try:
            service.update_value(setting.id, value=value)
        except Exception:
            failed_keys.append(key)

    return failed_keys, deleted_keys


def get_settings_raw() -> list[dict[str, Any]]:
    all_settings = service.list_settings()
    # Convert records to dicts for template compatibility
    settings_list = [s.to_dict() for s in all_settings]
    # Add key and value_type to dict for template
    for i, s in enumerate(all_settings):
        settings_list[i]["key"] = s.key
        settings_list[i]["value_type"] = s.value_type
    return settings_list


def _parse_setting_value(v_type: str, raw_val: str) -> tuple[Any, bool]:
    """Parse a setting value from form input.

    Returns:
        tuple of (parsed_value, success)
    """
    if v_type == "boolean":
        return 1 if raw_val == "on" else 0, True
    elif v_type == "integer":
        try:
            return int(raw_val), True
        except ValueError:
            return 0, True
    elif v_type == "json":
        try:
            return json.loads(raw_val), True
        except Exception:
            return None, False
    else:
        return raw_val, True


class SettingsRoutes:
    def __init__(self) -> None:
        self.bp = Blueprint("settings", __name__, url_prefix="/settings")
        self._setup_routes()

    def _setup_routes(self) -> None:
        @self.bp.route("/", methods=["GET"])
        @admin_required
        def dashboard():
            settings_list = get_settings_raw()
            return render_template(
                "admins/settings.html",
                settings_list=settings_list,
            )

        @self.bp.post("/create")
        @admin_required
        def create():
            key = request.form.get("key", "").strip()
            title = request.form.get("title", "").strip()
            value_type = request.form.get("value_type", "boolean").strip()

            if not re.fullmatch(r"[a-z][a-z0-9_]{0,189}", key):
                flash(
                    "Key must start with a lowercase letter and contain only lowercase letters, digits, and underscores.",
                    "danger",
                )
                return redirect(url_for("admin.settings.dashboard"))

            if key and title:
                try:
                    service.create_setting(key, title, value_type)
                    flash("Setting created successfully.", "success")
                except ValueError as e:
                    flash(f"Setting could not be created: {e}", "danger")
            else:
                flash("Key and Title are required.", "danger")

            return redirect(url_for("admin.settings.dashboard"))

        @self.bp.post("/update")
        @admin_required
        def update():
            failed_keys, deleted_keys = settings_update_form(request.form)
            # Invalidate runtime cache only if all updates succeeded
            if not failed_keys:
                if deleted_keys:
                    flash(f"Deleted settings: {', '.join(deleted_keys)}. ", "success")

                flash("Settings updated successfully.", "success")
            else:
                flash(f"Some settings failed to update: {', '.join(failed_keys)}", "danger")
            return redirect(url_for("admin.settings.dashboard"))


settings_module = SettingsRoutes()

__all__ = [
    "settings_module",
]
