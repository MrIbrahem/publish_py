"""Utilities for managing language settings."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ....shared.domain.db_service import has_db_config
from ..db.db_language_settings import LanguageSettingsDB
from ..models.language_setting import LanguageSettingRecord

logger = logging.getLogger(__name__)

_LANGUAGE_SETTINGS_STORE: LanguageSettingsDB | None = None


def get_language_settings_db() -> LanguageSettingsDB:
    global _LANGUAGE_SETTINGS_STORE

    if _LANGUAGE_SETTINGS_STORE is None:
        if not has_db_config():
            raise RuntimeError("LanguageSettingsDB requires database configuration; no fallback store is available.")

        try:
            _LANGUAGE_SETTINGS_STORE = LanguageSettingsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL LanguageSettingsDB")
            raise RuntimeError("Unable to initialize LanguageSettingsDB") from exc

    return _LANGUAGE_SETTINGS_STORE


def list_language_settings() -> List[LanguageSettingRecord]:
    """Return all language setting records."""
    store = get_language_settings_db()
    return store.list()


def get_language_setting(setting_id: int) -> LanguageSettingRecord | None:
    """Get a language setting record by ID."""
    store = get_language_settings_db()
    return store.fetch_by_id(setting_id)


def get_language_setting_by_code(lang_code: str) -> LanguageSettingRecord | None:
    """Get a language setting record by language code."""
    store = get_language_settings_db()
    return store.fetch_by_lang_code(lang_code)


def add_language_setting(
    lang_code: str,
    move_dots: int = 0,
    expend: int = 0,
    add_en_lang: int = 0,
    add_en_lng: int = 0,
) -> LanguageSettingRecord:
    """Add a new language setting record."""
    store = get_language_settings_db()
    return store.add(lang_code, move_dots, expend, add_en_lang, add_en_lng)


def add_or_update_language_setting(
    lang_code: str,
    move_dots: int = 0,
    expend: int = 0,
    add_en_lang: int = 0,
    add_en_lng: int = 0,
) -> LanguageSettingRecord:
    """Add or update a language setting record."""
    store = get_language_settings_db()
    return store.add_or_update(lang_code, move_dots, expend, add_en_lang, add_en_lng)


def update_language_setting(setting_id: int, **kwargs) -> LanguageSettingRecord:
    """Update a language setting record."""
    store = get_language_settings_db()
    return store.update(setting_id, **kwargs)


def delete_language_setting(setting_id: int) -> LanguageSettingRecord:
    """Delete a language setting record by ID."""
    store = get_language_settings_db()
    return store.delete(setting_id)


__all__ = [
    "get_language_settings_db",
    "list_language_settings",
    "get_language_setting",
    "get_language_setting_by_code",
    "add_language_setting",
    "add_or_update_language_setting",
    "update_language_setting",
    "delete_language_setting",
]
