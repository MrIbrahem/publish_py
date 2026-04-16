"""Database handler for mdwiki_revids table.

Stores MDWiki revision IDs for page titles.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ....shared.core.db_driver import Database
from ..models.mdwiki_revid import MdwikiRevidRecord

logger = logging.getLogger(__name__)


class MdwikiRevidsDB:
    """MySQL-backed database handler for mdwiki_revids table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> MdwikiRevidRecord:
        return MdwikiRevidRecord(**row)

    def fetch_by_title(self, title: str) -> MdwikiRevidRecord | None:
        """Get an mdwiki_revid record by title."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM mdwiki_revids WHERE title = %s",
            (title,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[MdwikiRevidRecord]:
        """Return all mdwiki_revid records."""
        rows = self.db.fetch_query_safe("SELECT * FROM mdwiki_revids ORDER BY title ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, title: str, revid: int) -> MdwikiRevidRecord:
        """Add a new mdwiki_revid record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        try:
            self.db.execute_query(
                "INSERT INTO mdwiki_revids (title, revid) VALUES (%s, %s)",
                (title, revid),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"MDWiki revid for '{title}' already exists") from None

        record = self.fetch_by_title(title)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created mdwiki_revid for '{title}'")
        return record

    def update(self, title: str, revid: int) -> MdwikiRevidRecord:
        """Update an mdwiki_revid record."""
        record = self.fetch_by_title(title)
        if not record:
            raise ValueError(f"MDWiki revid record for '{title}' not found")

        self.db.execute_query_safe(
            "UPDATE mdwiki_revids SET revid = %s WHERE title = %s",
            (revid, title),
        )
        updated = self.fetch_by_title(title)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated mdwiki_revid for '{title}'")
        return updated

    def delete(self, title: str) -> MdwikiRevidRecord:
        """Delete an mdwiki_revid record by title."""
        record = self.fetch_by_title(title)
        if not record:
            raise ValueError(f"MDWiki revid record for '{title}' not found")

        self.db.execute_query_safe(
            "DELETE FROM mdwiki_revids WHERE title = %s",
            (title,),
        )
        return record

    def add_or_update(self, title: str, revid: int) -> MdwikiRevidRecord:
        """Add or update an mdwiki_revid record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        self.db.execute_query_safe(
            """
            INSERT INTO mdwiki_revids (title, revid)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                revid = VALUES(revid)
            """,
            (title, revid),
        )
        record = self.fetch_by_title(title)
        if not record:
            raise RuntimeError(f"Failed to fetch mdwiki_revid for '{title}' after add_or_update")
        return record


__all__ = [
    "MdwikiRevidsDB",
]
