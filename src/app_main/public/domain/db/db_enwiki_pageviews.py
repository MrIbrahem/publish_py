"""Database handler for enwiki_pageviews table.

Stores English Wikipedia pageview counts.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ....shared.core.db_driver import Database
from .....db_models.public_models import EnwikiPageviewRecord

logger = logging.getLogger(__name__)


class EnwikiPageviewsDB:
    """MySQL-backed database handler for enwiki_pageviews table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> EnwikiPageviewRecord:
        return EnwikiPageviewRecord(**row)

    def fetch_by_id(self, pageview_id: int) -> EnwikiPageviewRecord | None:
        """Get an enwiki pageview record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM enwiki_pageviews WHERE id = %s",
            (pageview_id,),
        )
        if not rows:
            logger.warning(f"Enwiki pageview record with ID {pageview_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_title(self, title: str) -> EnwikiPageviewRecord | None:
        """Get an enwiki pageview record by title."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM enwiki_pageviews WHERE title = %s",
            (title,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[EnwikiPageviewRecord]:
        """Return all enwiki pageview records."""
        rows = self.db.fetch_query_safe("SELECT * FROM enwiki_pageviews ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_by_views(self, limit: int = 100) -> List[EnwikiPageviewRecord]:
        """Return top records by view count."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM enwiki_pageviews ORDER BY en_views DESC LIMIT %s",
            (limit,),
        )
        return [self._row_to_record(row) for row in rows]

    def add(self, title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
        """Add a new enwiki pageview record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        try:
            self.db.execute_query(
                "INSERT INTO enwiki_pageviews (title, en_views) VALUES (%s, %s)",
                (title, en_views),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Enwiki pageview for '{title}' already exists") from None

        record = self.fetch_by_title(title)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created enwiki pageview for '{title}'")
        return record

    def update(self, pageview_id: int, **kwargs) -> EnwikiPageviewRecord:
        """Update an enwiki pageview record."""
        record = self.fetch_by_id(pageview_id)
        if not record:
            raise ValueError(f"Enwiki pageview record with ID {pageview_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [pageview_id]

        self.db.execute_query_safe(
            f"UPDATE enwiki_pageviews SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(pageview_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated enwiki pageview with ID {pageview_id}")
        return updated

    def delete(self, pageview_id: int) -> EnwikiPageviewRecord:
        """Delete an enwiki pageview record by ID."""
        record = self.fetch_by_id(pageview_id)
        if not record:
            raise ValueError(f"Enwiki pageview record with ID {pageview_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM enwiki_pageviews WHERE id = %s",
            (pageview_id,),
        )
        return record

    def add_or_update(self, title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
        """Add or update an enwiki pageview record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        self.db.execute_query_safe(
            """
            INSERT INTO enwiki_pageviews (title, en_views)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                en_views = VALUES(en_views)
            """,
            (title, en_views),
        )
        record = self.fetch_by_title(title)
        if not record:
            raise RuntimeError(f"Failed to fetch enwiki pageview for '{title}' after add_or_update")
        return record


__all__ = [
    "EnwikiPageviewsDB",
]
