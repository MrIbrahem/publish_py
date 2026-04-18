"""Database handler for users table.

Stores user records.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from .....db_models.public_models import UserRecord
from ....config import DbConfig
from ....shared.core.db_driver import Database

logger = logging.getLogger(__name__)


class UsersDB:
    """MySQL-backed database handler for users table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> UserRecord:
        return UserRecord(**row)

    def fetch_by_id(self, user_id: int) -> UserRecord | None:
        """Get a user record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM users WHERE user_id = %s",
            (user_id,),
        )
        if not rows:
            logger.warning(f"User record with ID {user_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_username(self, username: str) -> UserRecord | None:
        """Get a user record by username."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM users WHERE username = %s",
            (username,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[UserRecord]:
        """Return all user records."""
        rows = self.db.fetch_query_safe("SELECT * FROM users ORDER BY user_id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_by_group(self, user_group: str) -> List[UserRecord]:
        """Return user records by group."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM users WHERE user_group = %s ORDER BY user_id ASC",
            (user_group,),
        )
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        username: str,
        email: str = "",
        wiki: str = "",
        user_group: str = "Uncategorized",
    ) -> UserRecord:
        """Add a new user record."""
        username = username.strip()
        if not username:
            raise ValueError("Username is required")

        try:
            self.db.execute_query(
                """
                INSERT INTO users (username, email, wiki, user_group, reg_date)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (username, email, wiki, user_group),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"User '{username}' already exists") from None

        record = self.fetch_by_username(username)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created user '{username}'")
        return record

    def update(self, user_id: int, **kwargs) -> UserRecord:
        """Update a user record."""
        record = self.fetch_by_id(user_id)
        if not record:
            raise ValueError(f"User record with ID {user_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]

        self.db.execute_query_safe(
            f"UPDATE users SET {set_clause} WHERE user_id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(user_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated user with ID {user_id}")
        return updated

    def delete(self, user_id: int) -> UserRecord:
        """Delete a user record by ID."""
        record = self.fetch_by_id(user_id)
        if not record:
            raise ValueError(f"User record with ID {user_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM users WHERE user_id = %s",
            (user_id,),
        )
        return record

    def add_or_update(
        self,
        username: str,
        email: str = "",
        wiki: str = "",
        user_group: str = "Uncategorized",
    ) -> UserRecord:
        """Add or update a user record."""
        username = username.strip()
        if not username:
            raise ValueError("Username is required")

        self.db.execute_query_safe(
            """
            INSERT INTO users (username, email, wiki, user_group, reg_date)
            VALUES (%s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                email = VALUES(email),
                wiki = VALUES(wiki),
                user_group = VALUES(user_group)
            """,
            (username, email, wiki, user_group),
        )
        record = self.fetch_by_username(username)
        if not record:
            raise RuntimeError(f"Failed to fetch user '{username}' after add_or_update")
        return record


__all__ = [
    "UsersDB",
]
