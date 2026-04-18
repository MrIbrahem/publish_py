"""Database handler for translate_type table.

Stores translation type records.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from .....db_models.public_models import TranslateTypeRecord
from ....config import DbConfig
from ....shared.core.db_driver import Database

logger = logging.getLogger(__name__)


class TranslateTypeDB:
    """MySQL-backed database handler for translate_type table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> TranslateTypeRecord:
        return TranslateTypeRecord(**row)

    def fetch_by_id(self, tt_id: int) -> TranslateTypeRecord | None:
        """Get a translate_type record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM translate_type WHERE tt_id = %s",
            (tt_id,),
        )
        if not rows:
            logger.warning(f"TranslateType record with ID {tt_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_title(self, title: str) -> TranslateTypeRecord | None:
        """Get a translate_type record by title."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM translate_type WHERE tt_title = %s",
            (title,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[TranslateTypeRecord]:
        """Return all translate_type records."""
        rows = self.db.fetch_query_safe("SELECT * FROM translate_type ORDER BY tt_id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_lead_enabled(self) -> List[TranslateTypeRecord]:
        """Return translate_type records with lead enabled."""
        rows = self.db.fetch_query_safe("SELECT * FROM translate_type WHERE tt_lead = 1 ORDER BY tt_id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_full_enabled(self) -> List[TranslateTypeRecord]:
        """Return translate_type records with full enabled."""
        rows = self.db.fetch_query_safe("SELECT * FROM translate_type WHERE tt_full = 1 ORDER BY tt_id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        tt_title: str,
        tt_lead: int = 1,
        tt_full: int = 0,
    ) -> TranslateTypeRecord:
        """Add a new translate_type record."""
        tt_title = tt_title.strip()
        if not tt_title:
            raise ValueError("Title is required")

        try:
            self.db.execute_query(
                "INSERT INTO translate_type (tt_title, tt_lead, tt_full) VALUES (%s, %s, %s)",
                (tt_title, tt_lead, tt_full),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Translate type '{tt_title}' already exists") from None

        record = self.fetch_by_title(tt_title)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created translate_type '{tt_title}'")
        return record

    def update(self, tt_id: int, **kwargs) -> TranslateTypeRecord:
        """Update a translate_type record."""
        record = self.fetch_by_id(tt_id)
        if not record:
            raise ValueError(f"TranslateType record with ID {tt_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [tt_id]

        self.db.execute_query_safe(
            f"UPDATE translate_type SET {set_clause} WHERE tt_id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(tt_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated translate_type with ID {tt_id}")
        return updated

    def delete(self, tt_id: int) -> TranslateTypeRecord:
        """Delete a translate_type record by ID."""
        record = self.fetch_by_id(tt_id)
        if not record:
            raise ValueError(f"TranslateType record with ID {tt_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM translate_type WHERE tt_id = %s",
            (tt_id,),
        )
        return record

    def add_or_update(
        self,
        tt_title: str,
        tt_lead: int = 1,
        tt_full: int = 0,
    ) -> TranslateTypeRecord:
        """Add or update a translate_type record."""
        tt_title = tt_title.strip()
        if not tt_title:
            raise ValueError("Title is required")

        self.db.execute_query_safe(
            """
            INSERT INTO translate_type (tt_title, tt_lead, tt_full)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                tt_lead = VALUES(tt_lead),
                tt_full = VALUES(tt_full)
            """,
            (tt_title, tt_lead, tt_full),
        )
        record = self.fetch_by_title(tt_title)
        if not record:
            raise RuntimeError(f"Failed to fetch translate_type '{tt_title}' after add_or_update")
        return record


__all__ = [
    "TranslateTypeDB",
]
