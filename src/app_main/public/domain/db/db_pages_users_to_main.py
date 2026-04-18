"""Database handler for pages_users_to_main table.

Stores pages_users_to_main records.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from .....db_models.public_models import PagesUsersToMainRecord
from ....config import DbConfig
from ....shared.core.db_driver import Database

logger = logging.getLogger(__name__)


class PagesUsersToMainDB:
    """MySQL-backed database handler for pages_users_to_main table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> PagesUsersToMainRecord:
        return PagesUsersToMainRecord(**row)

    def fetch_by_id(self, record_id: int) -> PagesUsersToMainRecord | None:
        """Get a pages_users_to_main record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM pages_users_to_main WHERE id = %s",
            (record_id,),
        )
        if not rows:
            logger.warning(f"PagesUsersToMain record with ID {record_id} not found")
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[PagesUsersToMainRecord]:
        """Return all pages_users_to_main records."""
        rows = self.db.fetch_query_safe("SELECT * FROM pages_users_to_main ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        new_target: str = "",
        new_user: str = "",
        new_qid: str = "",
    ) -> PagesUsersToMainRecord:
        """Add a new pages_users_to_main record."""
        try:
            self.db.execute_query(
                """
                INSERT INTO pages_users_to_main (new_target, new_user, new_qid)
                VALUES (%s, %s, %s)
                """,
                (new_target, new_user, new_qid),
            )
        except pymysql.err.IntegrityError as e:
            raise ValueError(f"Failed to add pages_users_to_main record: {e}") from None

        # Fetch the last inserted record
        rows = self.db.fetch_query_safe(
            "SELECT * FROM pages_users_to_main WHERE new_target = %s AND new_user = %s ORDER BY id DESC LIMIT 1",
            (new_target, new_user),
        )
        if not rows:
            raise RuntimeError("Failed to fetch newly created pages_users_to_main record")
        return self._row_to_record(rows[0])

    def update(self, record_id: int, **kwargs) -> PagesUsersToMainRecord:
        """Update a pages_users_to_main record."""
        record = self.fetch_by_id(record_id)
        if not record:
            raise ValueError(f"PagesUsersToMain record with ID {record_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [record_id]

        self.db.execute_query_safe(
            f"UPDATE pages_users_to_main SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(record_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated pages_users_to_main with ID {record_id}")
        return updated

    def delete(self, record_id: int) -> PagesUsersToMainRecord:
        """Delete a pages_users_to_main record by ID."""
        record = self.fetch_by_id(record_id)
        if not record:
            raise ValueError(f"PagesUsersToMain record with ID {record_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM pages_users_to_main WHERE id = %s",
            (record_id,),
        )
        return record


__all__ = [
    "PagesUsersToMainDB",
]
