"""
TODO: should be updated to match php_src/bots/sql/db_Pages.php
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, List

import pymysql

from . import Database

logger = logging.getLogger(__name__)

table_creation_sql = """
CREATE TABLE IF NOT EXISTS `pages` (
    `id` int unsigned NOT NULL AUTO_INCREMENT,
    `title` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    `word` int DEFAULT NULL,
    `translate_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `cat` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `lang` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `user` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `target` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `date` date DEFAULT NULL,
    `pupdate` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `add_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `deleted` int DEFAULT '0',
    `mdwiki_revid` int DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_title` (`title`),
    KEY `target` (`target`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `pages_users` (
    `id` int unsigned NOT NULL AUTO_INCREMENT,
    `title` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    `word` int DEFAULT NULL,
    `translate_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `cat` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `lang` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `user` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `target` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `date` date DEFAULT NULL,
    `pupdate` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    `add_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `deleted` int DEFAULT '0',
    `mdwiki_revid` int DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_title` (`title`),
    KEY `target` (`target`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


@dataclass
class PageRecord:
    """Representation of a page."""

    id: int
    title: str
    word: int | None = None
    translate_type: str | None = None
    cat: str | None = None
    lang: str | None = None
    user: str | None = None
    target: str | None = None
    date: Any | None = None
    pupdate: str | None = None
    add_date: Any | None = None
    deleted: int = 0
    mdwiki_revid: int | None = None


class PagesDB:
    """MySQL-backed"""

    def __init__(self, db_data: dict[str, Any]):
        self.db = Database(db_data)
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.db.execute_query_safe(table_creation_sql)

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
            raise LookupError(f"Page {title!r} was not found")
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


__all__ = [
    "PagesDB",
    "PageRecord",
]
