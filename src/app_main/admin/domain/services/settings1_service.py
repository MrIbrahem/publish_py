"""

Utilities for managing settings.
TODO: this is copy of settings_service.py and should be work with the new SettingsDB1 and SettingRecord1.
"""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ....shared.domain.services.db_service import has_db_config
from ..db.db_settings1 import SettingsDB1
from ..models.setting1 import SettingRecord1

logger = logging.getLogger(__name__)

_SETTINGS_STORE: SettingsDB1 | None = None


def get_settings_db() -> SettingsDB1:
    global _SETTINGS_STORE

    if _SETTINGS_STORE is None:
        if not has_db_config():
            raise RuntimeError("SettingsDB1 requires database configuration; no fallback store is available.")

        try:
            _SETTINGS_STORE = SettingsDB1(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL SettingsDB1")
            raise RuntimeError("Unable to initialize SettingsDB1") from exc

    return _SETTINGS_STORE


def list_settings() -> List[SettingRecord1]:
    """Return all setting records."""
    store = get_settings_db()
    return store.list()


def list_active_settings() -> List[SettingRecord1]:
    """Return all non-ignored setting records."""
    store = get_settings_db()
    return store.list_active()


def get_setting(setting_id: int) -> SettingRecord1 | None:
    """Get a setting record by ID."""
    store = get_settings_db()
    return store.fetch_by_id(setting_id)


def get_setting_by_title(title: str) -> SettingRecord1 | None:
    """Get a setting record by title."""
    store = get_settings_db()
    return store.fetch_by_title(title)


def add_setting(
    title: str,
    displayed: str,
    form_type: str = "check",
    value: int = 0,
    ignored: int = 0,
) -> SettingRecord1:
    """Add a new setting record."""
    store = get_settings_db()
    return store.add(title, displayed, form_type, value, ignored)


def add_or_update_setting(
    title: str,
    displayed: str,
    form_type: str = "check",
    value: int = 0,
    ignored: int = 0,
) -> SettingRecord1:
    """Add or update a setting record."""
    store = get_settings_db()
    return store.add_or_update(title, displayed, form_type, value, ignored)


def update_setting(setting_id: int, **kwargs) -> SettingRecord1:
    """Update a setting record."""
    store = get_settings_db()
    return store.update(setting_id, **kwargs)


def delete_setting(setting_id: int) -> SettingRecord1:
    """Delete a setting record by ID."""
    store = get_settings_db()
    return store.delete(setting_id)


def get_setting_value(title: str, default: int = 0) -> int:
    """Get the value of a setting by title."""
    store = get_settings_db()
    record = store.fetch_by_title(title)
    return record.value if record else default


__all__ = [
    "get_settings_db",
    "list_settings",
    "list_active_settings",
    "get_setting",
    "get_setting_by_title",
    "add_setting",
    "add_or_update_setting",
    "update_setting",
    "delete_setting",
    "get_setting_value",
]
