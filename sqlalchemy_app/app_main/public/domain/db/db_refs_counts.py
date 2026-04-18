"""Database handler for refs_counts table.

Stores reference counts for pages.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ....shared.core.db_driver import Database
from ..models import RefsCountRecord

logger = logging.getLogger(__name__)


class RefsCountsDB:
    """MySQL-backed database handler for refs_counts table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> RefsCountRecord:
        return RefsCountRecord(**row)

    def fetch_by_id(self, refs_id: int) -> RefsCountRecord | None:
        """Get a refs_count record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM refs_counts WHERE r_id = %s",
            (refs_id,),
        )
        if not rows:
            logger.warning(f"RefsCount record with ID {refs_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_title(self, title: str) -> RefsCountRecord | None:
        """Get a refs_count record by title."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM refs_counts WHERE r_title = %s",
            (title,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[RefsCountRecord]:
        """Return all refs_count records."""
        rows = self.db.fetch_query_safe("SELECT * FROM refs_counts ORDER BY r_id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        r_title: str,
        r_lead_refs: int | None = None,
        r_all_refs: int | None = None,
    ) -> RefsCountRecord:
        """Add a new refs_count record."""
        r_title = r_title.strip()
        if not r_title:
            raise ValueError("Title is required")

        try:
            self.db.execute_query(
                "INSERT INTO refs_counts (r_title, r_lead_refs, r_all_refs) VALUES (%s, %s, %s)",
                (r_title, r_lead_refs, r_all_refs),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Refs count for '{r_title}' already exists") from None

        record = self.fetch_by_title(r_title)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created refs_count for '{r_title}'")
        return record

    def update(self, refs_id: int, **kwargs) -> RefsCountRecord:
        """Update a refs_count record."""
        record = self.fetch_by_id(refs_id)
        if not record:
            raise ValueError(f"RefsCount record with ID {refs_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [refs_id]

        self.db.execute_query_safe(
            f"UPDATE refs_counts SET {set_clause} WHERE r_id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(refs_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated refs_count with ID {refs_id}")
        return updated

    def delete(self, refs_id: int) -> RefsCountRecord:
        """Delete a refs_count record by ID."""
        record = self.fetch_by_id(refs_id)
        if not record:
            raise ValueError(f"RefsCount record with ID {refs_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM refs_counts WHERE r_id = %s",
            (refs_id,),
        )
        return record

    def add_or_update(
        self,
        r_title: str,
        r_lead_refs: int | None = None,
        r_all_refs: int | None = None,
    ) -> RefsCountRecord:
        """Add or update a refs_count record."""
        r_title = r_title.strip()
        if not r_title:
            raise ValueError("Title is required")

        self.db.execute_query_safe(
            """
            INSERT INTO refs_counts (r_title, r_lead_refs, r_all_refs)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                r_lead_refs = VALUES(r_lead_refs),
                r_all_refs = VALUES(r_all_refs)
            """,
            (r_title, r_lead_refs, r_all_refs),
        )
        record = self.fetch_by_title(r_title)
        if not record:
            raise RuntimeError(f"Failed to fetch refs_count for '{r_title}' after add_or_update")
        return record


__all__ = [
    "RefsCountsDB",
]
