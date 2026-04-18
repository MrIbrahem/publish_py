"""Database handler for users_no_inprocess table.

Stores users who should not appear in the in-process list.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from .....db_models.admin_models import UsersNoInprocessRecord
from ....config import DbConfig
from ....shared.core.db_driver import Database

logger = logging.getLogger(__name__)


class UsersNoInprocessDB:
    """MySQL-backed database handler for users_no_inprocess table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> UsersNoInprocessRecord:
        return UsersNoInprocessRecord(**row)

    def fetch_by_id(self, record_id: int) -> UsersNoInprocessRecord | None:
        """Get a users_no_inprocess record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM users_no_inprocess WHERE id = %s",
            (record_id,),
        )
        if not rows:
            logger.warning(f"UsersNoInprocess record with ID {record_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_user(self, user: str) -> UsersNoInprocessRecord | None:
        """Get a users_no_inprocess record by username."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM users_no_inprocess WHERE user = %s",
            (user,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[UsersNoInprocessRecord]:
        """Return all users_no_inprocess records."""
        rows = self.db.fetch_query_safe("SELECT * FROM users_no_inprocess ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_active(self) -> List[UsersNoInprocessRecord]:
        """Return all active users_no_inprocess records."""
        rows = self.db.fetch_query_safe("SELECT * FROM users_no_inprocess WHERE active = 1 ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, user: str, active: int = 1) -> UsersNoInprocessRecord:
        """Add a new users_no_inprocess record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        try:
            self.db.execute_query(
                "INSERT INTO users_no_inprocess (user, active) VALUES (%s, %s)",
                (user, active),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"UsersNoInprocess '{user}' already exists") from None

        record = self.fetch_by_user(user)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created users_no_inprocess '{user}'")
        return record

    def update(self, record_id: int, **kwargs) -> UsersNoInprocessRecord:
        """Update a users_no_inprocess record."""
        record = self.fetch_by_id(record_id)
        if not record:
            raise ValueError(f"UsersNoInprocess record with ID {record_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [record_id]

        self.db.execute_query_safe(
            f"UPDATE users_no_inprocess SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(record_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated users_no_inprocess with ID {record_id}")
        return updated

    def delete(self, record_id: int) -> UsersNoInprocessRecord:
        """Delete a users_no_inprocess record by ID."""
        record = self.fetch_by_id(record_id)
        if not record:
            raise ValueError(f"UsersNoInprocess record with ID {record_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM users_no_inprocess WHERE id = %s",
            (record_id,),
        )
        return record

    def add_or_update(self, user: str, active: int = 1) -> UsersNoInprocessRecord:
        """Add or update a users_no_inprocess record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        self.db.execute_query_safe(
            """
            INSERT INTO users_no_inprocess (user, active)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                active = VALUES(active)
            """,
            (user, active),
        )
        record = self.fetch_by_user(user)
        if not record:
            raise RuntimeError(f"Failed to fetch users_no_inprocess '{user}' after add_or_update")
        return record


__all__ = [
    "UsersNoInprocessDB",
]
