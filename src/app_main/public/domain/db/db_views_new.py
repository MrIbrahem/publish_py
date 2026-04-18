"""Database handler for views_new table.

Stores page view counts.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ....shared.core.db_driver import Database
from .....db_models.public_models import ViewsNewRecord

logger = logging.getLogger(__name__)


class ViewsNewDB:
    """MySQL-backed database handler for views_new table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> ViewsNewRecord:
        return ViewsNewRecord(**row)

    def fetch_by_id(self, view_id: int) -> ViewsNewRecord | None:
        """Get a views_new record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM views_new WHERE id = %s",
            (view_id,),
        )
        if not rows:
            logger.warning(f"ViewsNew record with ID {view_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_target_lang_year(self, target: str, lang: str, year: int) -> ViewsNewRecord | None:
        """Get a views_new record by target, language, and year."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM views_new WHERE target = %s AND lang = %s AND year = %s",
            (target, lang, year),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[ViewsNewRecord]:
        """Return all views_new records."""
        rows = self.db.fetch_query_safe("SELECT * FROM views_new ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def list_by_target(self, target: str) -> List[ViewsNewRecord]:
        """Return views_new records for a specific target."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM views_new WHERE target = %s ORDER BY year DESC",
            (target,),
        )
        return [self._row_to_record(row) for row in rows]

    def list_by_lang(self, lang: str) -> List[ViewsNewRecord]:
        """Return views_new records for a specific language."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM views_new WHERE lang = %s ORDER BY id ASC",
            (lang,),
        )
        return [self._row_to_record(row) for row in rows]

    def add(
        self,
        target: str,
        lang: str,
        year: int,
        views: int | None = 0,
    ) -> ViewsNewRecord:
        """Add a new views_new record."""
        target = target.strip()
        lang = lang.strip()

        if not target:
            raise ValueError("Target is required")
        if not lang:
            raise ValueError("Language is required")

        try:
            self.db.execute_query(
                "INSERT INTO views_new (target, lang, year, views) VALUES (%s, %s, %s, %s)",
                (target, lang, year, views),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Views record for '{target}' in '{lang}' for year {year} already exists") from None

        record = self.fetch_by_target_lang_year(target, lang, year)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created views_new record")
        return record

    def update(self, view_id: int, **kwargs) -> ViewsNewRecord:
        """Update a views_new record."""
        record = self.fetch_by_id(view_id)
        if not record:
            raise ValueError(f"ViewsNew record with ID {view_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [view_id]

        self.db.execute_query_safe(
            f"UPDATE views_new SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(view_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated views_new with ID {view_id}")
        return updated

    def delete(self, view_id: int) -> ViewsNewRecord:
        """Delete a views_new record by ID."""
        record = self.fetch_by_id(view_id)
        if not record:
            raise ValueError(f"ViewsNew record with ID {view_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM views_new WHERE id = %s",
            (view_id,),
        )
        return record

    def add_or_update(
        self,
        target: str,
        lang: str,
        year: int,
        views: int | None = 0,
    ) -> ViewsNewRecord:
        """Add or update a views_new record."""
        target = target.strip()
        lang = lang.strip()

        if not target:
            raise ValueError("Target is required")
        if not lang:
            raise ValueError("Language is required")

        self.db.execute_query_safe(
            """
            INSERT INTO views_new (target, lang, year, views)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                views = VALUES(views)
            """,
            (target, lang, year, views),
        )
        record = self.fetch_by_target_lang_year(target, lang, year)
        if not record:
            raise RuntimeError(f"Failed to fetch views_new record after add_or_update")
        return record


__all__ = [
    "ViewsNewDB",
]
