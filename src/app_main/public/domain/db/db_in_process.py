"""Database handler for in_process table.

Stores in-process translation records.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ....shared.core.db_driver import Database
from ..models.in_process import InProcessRecord

logger = logging.getLogger(__name__)


class InProcessDB:
    """MySQL-backed database handler for in_process table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> InProcessRecord:
        return InProcessRecord(**row)

    def fetch_by_id(self, process_id: int) -> InProcessRecord | None:
        """Get an in_process record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM in_process WHERE id = %s",
            (process_id,),
        )
        if not rows:
            logger.warning(f"In-process record with ID {process_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_title_user_lang(self, title: str, user: str, lang: str) -> InProcessRecord | None:
        """Get an in_process record by title, user, and language."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM in_process WHERE title = %s AND user = %s AND lang = %s",
            (title, user, lang),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[InProcessRecord]:
        """Return all in_process records."""
        rows = self.db.fetch_query_safe("SELECT * FROM in_process ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_by_user(self, user: str) -> List[InProcessRecord]:
        """Return in_process records for a specific user."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM in_process WHERE user = %s ORDER BY id ASC",
            (user,),
        )
        return [self._row_to_record(row) for row in rows]

    def list_by_lang(self, lang: str) -> List[InProcessRecord]:
        """Return in_process records for a specific language."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM in_process WHERE lang = %s ORDER BY id ASC",
            (lang,),
        )
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        title: str,
        user: str,
        lang: str,
        cat: str | None = "RTT",
        translate_type: str | None = "lead",
        word: int | None = 0,
    ) -> InProcessRecord:
        """Add a new in_process record."""
        title = title.strip()
        user = user.strip()
        lang = lang.strip()

        if not title:
            raise ValueError("Title is required")
        if not user:
            raise ValueError("User is required")
        if not lang:
            raise ValueError("Language is required")

        try:
            self.db.execute_query(
                """
                INSERT INTO in_process (title, user, lang, cat, translate_type, word, add_date)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (title, user, lang, cat, translate_type, word),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"In-process record for '{title}' by '{user}' in '{lang}' already exists") from None

        record = self.fetch_by_title_user_lang(title, user, lang)
        if not record:
            raise RuntimeError("Failed to fetch newly created in-process record")
        return record

    def update(self, process_id: int, **kwargs) -> InProcessRecord:
        """Update an in_process record."""
        record = self.fetch_by_id(process_id)
        if not record:
            raise ValueError(f"In-process record with ID {process_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [process_id]

        self.db.execute_query_safe(
            f"UPDATE in_process SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(process_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated in-process record with ID {process_id}")
        return updated

    def delete(self, process_id: int) -> InProcessRecord:
        """Delete an in_process record by ID."""
        record = self.fetch_by_id(process_id)
        if not record:
            raise ValueError(f"In-process record with ID {process_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM in_process WHERE id = %s",
            (process_id,),
        )
        return record

    def delete_by_title_user_lang(self, title: str, user: str, lang: str) -> bool:
        """Delete an in_process record by title, user, and language."""
        result = self.db.execute_query_safe(
            "DELETE FROM in_process WHERE title = %s AND user = %s AND lang = %s",
            (title, user, lang),
        )
        return result > 0


__all__ = [
    "InProcessDB",
]
