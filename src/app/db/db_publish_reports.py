"""
TODO: should mirror php_src/bots/sql/db_publish_reports.php
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, List

import pymysql

from . import Database

logger = logging.getLogger(__name__)


@dataclass
class PageRecord:
    """Representation of a page."""

    id: int
    title: str
    main_file: str | None
    created_at: Any | None = None
    updated_at: Any | None = None


class PagesDB:
    """MySQL-backed"""

    def __init__(self, db_data: dict[str, Any]):
        self.db = Database(db_data)
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.db.execute_query_safe(
            """
            CREATE TABLE IF NOT EXISTS `publish_reports` (
                `id` int NOT NULL AUTO_INCREMENT,
                `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                `user` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                `lang` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                `sourcetitle` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                `result` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                `data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
                PRIMARY KEY (`id`),
                CONSTRAINT `publish_reports_chk_1` CHECK (json_valid(`data`))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

            """
        )

    def _row_to_record(self, row: dict[str, Any]) -> PageRecord:
        return PageRecord(
            id=int(row["id"]),
            title=row["title"],
            main_file=row.get("main_file"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def _fetch_by_id(self, page_id: int) -> PageRecord:
        rows = self.db.fetch_query_safe(
            """
            SELECT id, title, main_file, created_at, updated_at
            FROM pages
            WHERE id = %s
            """,
            (page_id,),
        )
        if not rows:
            raise LookupError(f"Page id {page_id} was not found")
        return self._row_to_record(rows[0])

    def _fetch_by_title(self, title: str) -> PageRecord:
        rows = self.db.fetch_query_safe(
            """
            SELECT id, title, main_file, created_at, updated_at
            FROM pages
            WHERE title = %s
            """,
            (title,),
        )
        if not rows:
            raise LookupError(f"Page {title!r} was not found")
        return self._row_to_record(rows[0])

    def list(self) -> List[PageRecord]:
        rows = self.db.fetch_query_safe(
            """
            SELECT id, title, main_file, created_at, updated_at
            FROM pages
            ORDER BY id ASC
            """
        )
        return [self._row_to_record(row) for row in rows]

    def add(self, title: str, main_file: str) -> PageRecord:
        title = title.strip()
        main_file = main_file.strip()
        if not title:
            raise ValueError("Title is required")

        try:
            # Use execute_query to allow exception to propagate
            self.db.execute_query(
                """
                INSERT INTO pages (title, main_file) VALUES (%s, %s)
                """,
                (title, main_file),
            )
        except pymysql.err.IntegrityError:
            # This assumes a UNIQUE constraint on the title column
            raise ValueError(f"Page '{title}' already exists") from None

        return self._fetch_by_title(title)

    def update(self, page_id: int, title: str, main_file: str) -> PageRecord:
        _ = self._fetch_by_id(page_id)
        self.db.execute_query_safe(
            "UPDATE pages SET title = %s, main_file = %s WHERE id = %s",
            (title, main_file, page_id),
        )
        return self._fetch_by_id(page_id)

    def delete(self, page_id: int) -> PageRecord:
        record = self._fetch_by_id(page_id)
        self.db.execute_query_safe(
            "DELETE FROM pages WHERE id = %s",
            (page_id,),
        )
        return record

    def add_or_update(self, title: str, main_file: str) -> PageRecord:
        title = title.strip()
        main_file = main_file.strip()

        if not title:
            logger.error("Title is required for add_or_update")

        self.db.execute_query_safe(
            """
            INSERT INTO pages (title, main_file) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                title = COALESCE(VALUES(title), title),
                main_file = COALESCE(VALUES(main_file), main_file)
            """,
            (title, main_file),
        )
        return self._fetch_by_title(title)


__all__ = [
    "PagesDB",
    "PageRecord",
]
