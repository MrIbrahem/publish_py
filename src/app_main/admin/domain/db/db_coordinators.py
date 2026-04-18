"""Database handler for coordinators table.

Stores coordinator user records.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from .....db_models.admin_models import CoordinatorRecord
from ....config import DbConfig
from ....shared.core.db_driver import Database

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

    def fetch_by_user(self, username: str) -> CoordinatorRecord | None:
        """Get a coordinator record by username."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM coordinators WHERE username = %s",
            (username,),
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
        rows = self.db.fetch_query_safe("SELECT * FROM coordinators WHERE is_active = 1 ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, username: str, is_active: int = 1) -> CoordinatorRecord:
        """Add a new coordinator record."""
        username = username.strip()
        if not username:
            raise ValueError("User is required")

        try:
            self.db.execute_query(
                "INSERT INTO coordinators (username, is_active) VALUES (%s, %s)",
                (username, is_active),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Coordinator '{username}' already exists") from None

        record = self.fetch_by_user(username)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created coordinator '{username}'")
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

    def delete(self, coordinator_id: int) -> None:
        """Delete a coordinator record by ID."""
        record = self.fetch_by_id(coordinator_id)
        if not record:
            raise ValueError(f"Coordinator record with ID {coordinator_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM coordinators WHERE id = %s",
            (coordinator_id,),
        )

    def add_or_update(self, username: str, is_active: int = 1) -> CoordinatorRecord:
        """Add or update a coordinator record."""
        username = username.strip()
        if not username:
            raise ValueError("User is required")

        self.db.execute_query_safe(
            """
            INSERT INTO coordinators (username, is_active)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                is_active = VALUES(is_active)
            """,
            (username, is_active),
        )
        record = self.fetch_by_user(username)
        if not record:
            raise RuntimeError(f"Failed to fetch coordinator '{username}' after add_or_update")
        return record

    def set_active(self, coordinator_id: int, is_active: bool) -> CoordinatorRecord:
        _ = self.fetch_by_id(coordinator_id)
        self.db.execute_query_safe(
            "UPDATE coordinators SET is_active = %s WHERE id = %s",
            (1 if is_active else 0, coordinator_id),
        )
        return self.fetch_by_id(coordinator_id)


__all__ = [
    "CoordinatorsDB",
]
