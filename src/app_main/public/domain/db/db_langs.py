"""Database handler for langs table.

Stores language information.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ....shared.core.db_driver import Database
from ..models.lang import LangRecord

logger = logging.getLogger(__name__)


class LangsDB:
    """MySQL-backed database handler for langs table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> LangRecord:
        return LangRecord(**row)

    def fetch_by_id(self, lang_id: int) -> LangRecord | None:
        """Get a language record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM langs WHERE lang_id = %s",
            (lang_id,),
        )
        if not rows:
            logger.warning(f"Language record with ID {lang_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_code(self, code: str) -> LangRecord | None:
        """Get a language record by code."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM langs WHERE code = %s",
            (code,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[LangRecord]:
        """Return all language records."""
        rows = self.db.fetch_query_safe("SELECT * FROM langs ORDER BY lang_id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, code: str, autonym: str, name: str) -> LangRecord:
        """Add a new language record."""
        code = code.strip()
        if not code:
            raise ValueError("Language code is required")

        try:
            self.db.execute_query(
                "INSERT INTO langs (code, autonym, name) VALUES (%s, %s, %s)",
                (code, autonym, name),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Language '{code}' already exists") from None

        record = self.fetch_by_code(code)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created language '{code}'")
        return record

    def update(self, lang_id: int, **kwargs) -> LangRecord:
        """Update a language record."""
        record = self.fetch_by_id(lang_id)
        if not record:
            raise ValueError(f"Language record with ID {lang_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [lang_id]

        self.db.execute_query_safe(
            f"UPDATE langs SET {set_clause} WHERE lang_id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(lang_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated language with ID {lang_id}")
        return updated

    def delete(self, lang_id: int) -> LangRecord:
        """Delete a language record by ID."""
        record = self.fetch_by_id(lang_id)
        if not record:
            raise ValueError(f"Language record with ID {lang_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM langs WHERE lang_id = %s",
            (lang_id,),
        )
        return record

    def add_or_update(self, code: str, autonym: str, name: str) -> LangRecord:
        """Add or update a language record."""
        code = code.strip()
        if not code:
            raise ValueError("Language code is required")

        self.db.execute_query_safe(
            """
            INSERT INTO langs (code, autonym, name)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                autonym = VALUES(autonym),
                name = VALUES(name)
            """,
            (code, autonym, name),
        )
        record = self.fetch_by_code(code)
        if not record:
            raise RuntimeError(f"Failed to fetch language '{code}' after add_or_update")
        return record


__all__ = [
    "LangsDB",
]
