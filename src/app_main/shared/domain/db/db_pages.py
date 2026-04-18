""" """

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ...core.db_driver import Database
from .....db_models.shared_models import PageRecord

logger = logging.getLogger(__name__)


class PagesDB:
    """MySQL-backed"""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> PageRecord:
        return PageRecord(**row)

    def _fetch_by_id(self, page_id: int) -> PageRecord:
        rows = self.db.fetch_query_safe(
            "SELECT * FROM pages WHERE id = %s",
            (page_id,),
        )
        if not rows:
            raise LookupError(f"Page id {page_id} was not found")
        return self._row_to_record(rows[0])

    def _fetch_by_title(self, title: str) -> PageRecord:
        rows = self.db.fetch_query_safe(
            "SELECT * FROM pages WHERE title = %s",
            (title,),
        )
        if not rows:
            raise LookupError(f"Page {title} was not found")
        return self._row_to_record(rows[0])

    def list(self) -> List[PageRecord]:
        rows = self.db.fetch_query_safe("SELECT * FROM pages ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, title: str, **kwargs) -> PageRecord:
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        cols = ["title"] + list(kwargs.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        values = [title] + list(kwargs.values())

        try:
            self.db.execute_query(
                f"INSERT INTO pages ({', '.join(cols)}) VALUES ({placeholders})",
                tuple(values),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Page '{title}' already exists") from None

        return self._fetch_by_title(title)

    def update(self, page_id: int, **kwargs) -> PageRecord:
        # Validate that the record exists before attempting update
        _ = self._fetch_by_id(page_id)
        if not kwargs:
            return self._fetch_by_id(page_id)

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [page_id]

        self.db.execute_query_safe(
            f"UPDATE pages SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        return self._fetch_by_id(page_id)

    def delete(self, page_id: int) -> PageRecord:
        record = self._fetch_by_id(page_id)
        self.db.execute_query_safe(
            "DELETE FROM pages WHERE id = %s",
            (page_id,),
        )
        return record

    def add_or_update(self, title: str, **kwargs) -> PageRecord:
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        cols = ["title"] + list(kwargs.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        updates = ", ".join([f"`{col}` = VALUES(`{col}`)" for col in kwargs.keys()])
        values = [title] + list(kwargs.values())

        sql = f"INSERT INTO pages ({', '.join(cols)}) VALUES ({placeholders})"
        if updates:
            sql += f" ON DUPLICATE KEY UPDATE {updates}"

        self.db.execute_query_safe(sql, tuple(values))
        return self._fetch_by_title(title)

    def _find_exists_or_update(
        self,
        title: str,
        lang: str,
        user: str,
        target: str,
    ) -> bool:
        """Check if record exists and update target if empty."""
        query = "SELECT * FROM pages WHERE title = %s AND lang = %s AND user = %s"
        result = self.db.fetch_query_safe(query, (title, lang, user))

        if result:
            update_query = """
                UPDATE pages SET target = %s, pupdate = DATE(NOW())
                WHERE title = %s AND lang = %s AND user = %s AND (target = '' OR target IS NULL)
            """
            self.db.execute_query_safe(update_query, (target, title, lang, user))

        return len(result) > 0

    def insert_page_target(
        self,
        sourcetitle: str,
        tr_type: str,
        cat: str,
        lang: str,
        user: str,
        target: str,
        mdwiki_revid: int | None = None,
        word: int = 0,
    ) -> bool:
        """
        Insert a page target record.

        Mirrors: php_src/bots/sql/db_pages.php InsertPageTarget()

        Args:
            sourcetitle: Page title
            tr_type: Translation type
            cat: Category
            lang: Target language
            user: Username
            target: Target page title
            mdwiki_revid: MDWiki revision ID
            word: Word count
        """

        query = """
            INSERT INTO pages (title, word, translate_type, cat, lang, user, pupdate, target, mdwiki_revid)
            VALUES (%s, %s, %s, %s, %s, %s, DATE(NOW()), %s, %s)
        """
        params = (sourcetitle, word, tr_type, cat, lang, user, target, mdwiki_revid)

        try:
            self.db.execute_query_safe(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to insert page target: {e}")
            return False


__all__ = [
    "PagesDB",
]
