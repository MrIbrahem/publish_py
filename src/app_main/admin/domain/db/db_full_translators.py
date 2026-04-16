"""Database handler for full_translators table.

Stores full translator user records.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ....shared.core.db_driver import Database
from ..models.full_translator import FullTranslatorRecord

logger = logging.getLogger(__name__)


class FullTranslatorsDB:
    """MySQL-backed database handler for full_translators table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> FullTranslatorRecord:
        return FullTranslatorRecord(**row)

    def fetch_by_id(self, translator_id: int) -> FullTranslatorRecord | None:
        """Get a full translator record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM full_translators WHERE id = %s",
            (translator_id,),
        )
        if not rows:
            logger.warning(f"Full translator record with ID {translator_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_user(self, user: str) -> FullTranslatorRecord | None:
        """Get a full translator record by username."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM full_translators WHERE user = %s",
            (user,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[FullTranslatorRecord]:
        """Return all full translator records."""
        rows = self.db.fetch_query_safe("SELECT * FROM full_translators ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_active(self) -> List[FullTranslatorRecord]:
        """Return all active full translator records."""
        rows = self.db.fetch_query_safe("SELECT * FROM full_translators WHERE active = 1 ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, user: str, active: int = 1) -> FullTranslatorRecord:
        """Add a new full translator record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        try:
            self.db.execute_query(
                "INSERT INTO full_translators (user, active) VALUES (%s, %s)",
                (user, active),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Full translator '{user}' already exists") from None

        record = self.fetch_by_user(user)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created full translator '{user}'")
        return record

    def update(self, translator_id: int, **kwargs) -> FullTranslatorRecord:
        """Update a full translator record."""
        record = self.fetch_by_id(translator_id)
        if not record:
            raise ValueError(f"Full translator record with ID {translator_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [translator_id]

        self.db.execute_query_safe(
            f"UPDATE full_translators SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(translator_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated full translator with ID {translator_id}")
        return updated

    def delete(self, translator_id: int) -> FullTranslatorRecord:
        """Delete a full translator record by ID."""
        record = self.fetch_by_id(translator_id)
        if not record:
            raise ValueError(f"Full translator record with ID {translator_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM full_translators WHERE id = %s",
            (translator_id,),
        )
        return record

    def add_or_update(self, user: str, active: int = 1) -> FullTranslatorRecord:
        """Add or update a full translator record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        self.db.execute_query_safe(
            """
            INSERT INTO full_translators (user, active)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                active = VALUES(active)
            """,
            (user, active),
        )
        record = self.fetch_by_user(user)
        if not record:
            raise RuntimeError(f"Failed to fetch full translator '{user}' after add_or_update")
        return record


__all__ = [
    "FullTranslatorsDB",
]
