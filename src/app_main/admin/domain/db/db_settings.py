"""Database handler for settings table.

Stores application settings.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ....shared.core.db_driver import Database
from ..models.setting import SettingRecord

logger = logging.getLogger(__name__)


class SettingsDB:
    """MySQL-backed database handler for settings table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> SettingRecord:
        return SettingRecord(**row)

    def fetch_by_id(self, setting_id: int) -> SettingRecord | None:
        """Get a setting record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM settings WHERE id = %s",
            (setting_id,),
        )
        if not rows:
            logger.warning(f"Setting record with ID {setting_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_title(self, title: str) -> SettingRecord | None:
        """Get a setting record by title."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM settings WHERE title = %s",
            (title,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[SettingRecord]:
        """Return all setting records."""
        rows = self.db.fetch_query_safe("SELECT * FROM settings ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_active(self) -> List[SettingRecord]:
        """Return all non-ignored setting records."""
        rows = self.db.fetch_query_safe("SELECT * FROM settings WHERE ignored = 0 ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        title: str,
        displayed: str,
        Type: str = "check",
        value: int = 0,
        ignored: int = 0,
    ) -> SettingRecord:
        """Add a new setting record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        try:
            self.db.execute_query(
                """
                INSERT INTO settings (title, displayed, Type, value, ignored)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (title, displayed, Type, value, ignored),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Setting '{title}' already exists") from None

        record = self.fetch_by_title(title)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created setting '{title}'")
        return record

    def update(self, setting_id: int, **kwargs) -> SettingRecord:
        """Update a setting record."""
        record = self.fetch_by_id(setting_id)
        if not record:
            raise ValueError(f"Setting record with ID {setting_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [setting_id]

        self.db.execute_query_safe(
            f"UPDATE settings SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(setting_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated setting with ID {setting_id}")
        return updated

    def delete(self, setting_id: int) -> SettingRecord:
        """Delete a setting record by ID."""
        record = self.fetch_by_id(setting_id)
        if not record:
            raise ValueError(f"Setting record with ID {setting_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM settings WHERE id = %s",
            (setting_id,),
        )
        return record

    def add_or_update(
        self,
        title: str,
        displayed: str,
        Type: str = "check",
        value: int = 0,
        ignored: int = 0,
    ) -> SettingRecord:
        """Add or update a setting record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        self.db.execute_query_safe(
            """
            INSERT INTO settings (title, displayed, Type, value, ignored)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                displayed = VALUES(displayed),
                Type = VALUES(Type),
                value = VALUES(value),
                ignored = VALUES(ignored)
            """,
            (title, displayed, Type, value, ignored),
        )
        record = self.fetch_by_title(title)
        if not record:
            raise RuntimeError(f"Failed to fetch setting '{title}' after add_or_update")
        return record


__all__ = [
    "SettingsDB",
]
