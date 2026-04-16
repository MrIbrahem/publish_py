"""Utilities for managing settings1 (key-value settings with type support)."""

from __future__ import annotations

import logging
from typing import Any, List

from ....config import settings
from ....shared.domain.services.db_service import has_db_config
from ..db.db_settings import SettingsDB
from ..models.setting import SettingRecord

logger = logging.getLogger(__name__)

_SETTINGS_STORE: SettingsDB | None = None


def get_settings_db() -> SettingsDB:
    global _SETTINGS_STORE

    if _SETTINGS_STORE is None:
        if not has_db_config():
            raise RuntimeError("SettingsDB requires database configuration; no fallback store is available.")

        try:
            _SETTINGS_STORE = SettingsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL SettingsDB")
            raise RuntimeError("Unable to initialize SettingsDB") from exc

    return _SETTINGS_STORE


def list_settings() -> List[SettingRecord]:
    """Return all setting records."""
    store = get_settings_db()
    return store.list()


def get_setting(setting_id: int) -> SettingRecord | None:
    """Get a setting record by ID."""
    store = get_settings_db()
    return store.fetch_by_id(setting_id)


def get_setting_by_key(key: str) -> SettingRecord | None:
    """Get a setting record by key."""
    store = get_settings_db()
    return store.fetch_by_key(key)


def add_setting(
    key: str,
    title: str,
    value_type: str = "boolean",
    value: Any = None,
) -> SettingRecord:
    """Add a new setting record."""
    store = get_settings_db()
    return store.add(key, title, value_type, value)


def update_value(setting_id: int, value: Any) -> SettingRecord:
    """Update a setting record."""
    store = get_settings_db()
    return store.update_value(setting_id, value)


def delete_setting(setting_id: int) -> SettingRecord:
    """Delete a setting record by ID."""
    store = get_settings_db()
    return store.delete(setting_id)


__all__ = [
    "get_settings_db",
    "list_settings",
    "get_setting",
    "get_setting_by_key",
    "add_setting",
    "update_value",
    "delete_setting",
]
