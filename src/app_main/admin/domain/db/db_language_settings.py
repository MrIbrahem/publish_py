"""Database handler for language_settings table.

Stores language-specific settings.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from .....config import DbConfig
from ....shared.core.db_driver import Database
from ..models.language_setting import LanguageSettingRecord

logger = logging.getLogger(__name__)


class LanguageSettingsDB:
    """MySQL-backed database handler for language_settings table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> LanguageSettingRecord:
        return LanguageSettingRecord(**row)

    def fetch_by_id(self, setting_id: int) -> LanguageSettingRecord | None:
        """Get a language setting record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM language_settings WHERE id = %s",
            (setting_id,),
        )
        if not rows:
            logger.warning(f"Language setting record with ID {setting_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_lang_code(self, lang_code: str) -> LanguageSettingRecord | None:
        """Get a language setting record by language code."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM language_settings WHERE lang_code = %s",
            (lang_code,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[LanguageSettingRecord]:
        """Return all language setting records."""
        rows = self.db.fetch_query_safe("SELECT * FROM language_settings ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        lang_code: str,
        move_dots: int = 0,
        expend: int = 0,
        add_en_lang: int = 0,
        add_en_lng: int = 0,
    ) -> LanguageSettingRecord:
        """Add a new language setting record."""
        lang_code = lang_code.strip()
        if not lang_code:
            raise ValueError("Language code is required")

        try:
            self.db.execute_query(
                """
                INSERT INTO language_settings (lang_code, move_dots, expend, add_en_lang, add_en_lng)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (lang_code, move_dots, expend, add_en_lang, add_en_lng),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Language setting for '{lang_code}' already exists") from None

        record = self.fetch_by_lang_code(lang_code)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created language setting for '{lang_code}'")
        return record

    def update(self, setting_id: int, **kwargs) -> LanguageSettingRecord:
        """Update a language setting record."""
        record = self.fetch_by_id(setting_id)
        if not record:
            raise ValueError(f"Language setting record with ID {setting_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [setting_id]

        self.db.execute_query_safe(
            f"UPDATE language_settings SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(setting_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated language setting with ID {setting_id}")
        return updated

    def delete(self, setting_id: int) -> LanguageSettingRecord:
        """Delete a language setting record by ID."""
        record = self.fetch_by_id(setting_id)
        if not record:
            raise ValueError(f"Language setting record with ID {setting_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM language_settings WHERE id = %s",
            (setting_id,),
        )
        return record

    def add_or_update(
        self,
        lang_code: str,
        move_dots: int = 0,
        expend: int = 0,
        add_en_lang: int = 0,
        add_en_lng: int = 0,
    ) -> LanguageSettingRecord:
        """Add or update a language setting record."""
        lang_code = lang_code.strip()
        if not lang_code:
            raise ValueError("Language code is required")

        self.db.execute_query_safe(
            """
            INSERT INTO language_settings (lang_code, move_dots, expend, add_en_lang, add_en_lng)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                move_dots = VALUES(move_dots),
                expend = VALUES(expend),
                add_en_lang = VALUES(add_en_lang),
                add_en_lng = VALUES(add_en_lng)
            """,
            (lang_code, move_dots, expend, add_en_lang, add_en_lng),
        )
        record = self.fetch_by_lang_code(lang_code)
        if not record:
            raise RuntimeError(f"Failed to fetch language setting for '{lang_code}' after add_or_update")
        return record


__all__ = [
    "LanguageSettingsDB",
]
