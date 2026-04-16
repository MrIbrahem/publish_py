"""Database handler for coordinators table.

Stores coordinator user records.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from .....config import DbConfig
from ....shared.core.db_driver import Database
from ..models.coordinator import CoordinatorRecord

logger = logging.getLogger(__name__)


class CoordinatorsDB:
    """MySQL-backed database handler for coordinators table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> CoordinatorRecord:
        return CoordinatorRecord(**row)

    def fetch_by_id(self, coordinator_id: int) -> CoordinatorRecord | None:
        """Get a coordinator record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM coordinators WHERE id = %s",
            (coordinator_id,),
        )
        if not rows:
            logger.warning(f"Coordinator record with ID {coordinator_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_user(self, user: str) -> CoordinatorRecord | None:
        """Get a coordinator record by username."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM coordinators WHERE user = %s",
            (user,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[CoordinatorRecord]:
        """Return all coordinator records."""
        rows = self.db.fetch_query_safe("SELECT * FROM coordinators ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_active(self) -> List[CoordinatorRecord]:
        """Return all active coordinator records."""
        rows = self.db.fetch_query_safe("SELECT * FROM coordinators WHERE active = 1 ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, user: str, active: int = 1) -> CoordinatorRecord:
        """Add a new coordinator record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        try:
            self.db.execute_query(
                "INSERT INTO coordinators (user, active) VALUES (%s, %s)",
                (user, active),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Coordinator '{user}' already exists") from None

        record = self.fetch_by_user(user)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created coordinator '{user}'")
        return record

    def update(self, coordinator_id: int, **kwargs) -> CoordinatorRecord:
        """Update a coordinator record."""
        record = self.fetch_by_id(coordinator_id)
        if not record:
            raise ValueError(f"Coordinator record with ID {coordinator_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [coordinator_id]

        self.db.execute_query_safe(
            f"UPDATE coordinators SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(coordinator_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated coordinator with ID {coordinator_id}")
        return updated

    def delete(self, coordinator_id: int) -> CoordinatorRecord:
        """Delete a coordinator record by ID."""
        record = self.fetch_by_id(coordinator_id)
        if not record:
            raise ValueError(f"Coordinator record with ID {coordinator_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM coordinators WHERE id = %s",
            (coordinator_id,),
        )
        return record

    def add_or_update(self, user: str, active: int = 1) -> CoordinatorRecord:
        """Add or update a coordinator record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        self.db.execute_query_safe(
            """
            INSERT INTO coordinators (user, active)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                active = VALUES(active)
            """,
            (user, active),
        )
        record = self.fetch_by_user(user)
        if not record:
            raise RuntimeError(f"Failed to fetch coordinator '{user}' after add_or_update")
        return record


__all__ = [
    "CoordinatorsDB",
]
