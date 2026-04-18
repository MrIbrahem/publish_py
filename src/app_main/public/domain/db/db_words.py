"""Database handler for words table.

Stores word counts for pages.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from .....db_models.public_models import WordRecord
from ....config import DbConfig
from ....shared.core.db_driver import Database

logger = logging.getLogger(__name__)


class WordsDB:
    """MySQL-backed database handler for words table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> WordRecord:
        return WordRecord(**row)

    def fetch_by_id(self, word_id: int) -> WordRecord | None:
        """Get a word record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM words WHERE w_id = %s",
            (word_id,),
        )
        if not rows:
            logger.warning(f"Word record with ID {word_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_title(self, title: str) -> WordRecord | None:
        """Get a word record by title."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM words WHERE w_title = %s",
            (title,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[WordRecord]:
        """Return all word records."""
        rows = self.db.fetch_query_safe("SELECT * FROM words ORDER BY w_id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        w_title: str,
        w_lead_words: int | None = None,
        w_all_words: int | None = None,
    ) -> WordRecord:
        """Add a new word record."""
        w_title = w_title.strip()
        if not w_title:
            raise ValueError("Title is required")

        try:
            self.db.execute_query(
                "INSERT INTO words (w_title, w_lead_words, w_all_words) VALUES (%s, %s, %s)",
                (w_title, w_lead_words, w_all_words),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Word count for '{w_title}' already exists") from None

        record = self.fetch_by_title(w_title)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created word record for '{w_title}'")
        return record

    def update(self, word_id: int, **kwargs) -> WordRecord:
        """Update a word record."""
        record = self.fetch_by_id(word_id)
        if not record:
            raise ValueError(f"Word record with ID {word_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [word_id]

        self.db.execute_query_safe(
            f"UPDATE words SET {set_clause} WHERE w_id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(word_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated word record with ID {word_id}")
        return updated

    def delete(self, word_id: int) -> WordRecord:
        """Delete a word record by ID."""
        record = self.fetch_by_id(word_id)
        if not record:
            raise ValueError(f"Word record with ID {word_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM words WHERE w_id = %s",
            (word_id,),
        )
        return record

    def add_or_update(
        self,
        w_title: str,
        w_lead_words: int | None = None,
        w_all_words: int | None = None,
    ) -> WordRecord:
        """Add or update a word record."""
        w_title = w_title.strip()
        if not w_title:
            raise ValueError("Title is required")

        self.db.execute_query_safe(
            """
            INSERT INTO words (w_title, w_lead_words, w_all_words)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                w_lead_words = VALUES(w_lead_words),
                w_all_words = VALUES(w_all_words)
            """,
            (w_title, w_lead_words, w_all_words),
        )
        record = self.fetch_by_title(w_title)
        if not record:
            raise RuntimeError(f"Failed to fetch word record for '{w_title}' after add_or_update")
        return record


__all__ = [
    "WordsDB",
]
