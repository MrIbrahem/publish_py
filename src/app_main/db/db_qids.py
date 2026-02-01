"""
Database handler for qids table.

Stores Wikidata QIDs for MDWiki page titles.
"""

from __future__ import annotations

import logging
from typing import Any

from ..config import DbConfig

from . import Database

logger = logging.getLogger(__name__)

qids_table_creation_sql = """
CREATE TABLE IF NOT EXISTS `qids` (
    `id` int unsigned NOT NULL AUTO_INCREMENT,
    `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    `qid` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
    `add_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `title` (`title`),
    KEY `qid` (`qid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


def ensure_qids_table(db_data: DbConfig) -> bool:
    """Create the qids table if it does not already exist.

    Args:
        db_data: Database connection configuration

    Returns:
        True if table was ensured successfully, False otherwise
    """
    try:
        db = Database(db_data)
        db.execute_query_safe(qids_table_creation_sql)
        logger.debug("qids table ensured")
        return True
    except Exception as e:
        logger.error(f"Failed to ensure qids table: {e}")
        return False


class QidsDB:
    """MySQL-backed database handler for qids table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.db.execute_query_safe(qids_table_creation_sql)

    def get_qid_by_title(self, title: str) -> str | None:
        """Get QID for a given title.

        Args:
            title: MDWiki page title

        Returns:
            QID string or None if not found
        """
        rows = self.db.fetch_query_safe(
            "SELECT qid FROM qids WHERE title = %s",
            (title,),
        )
        if rows:
            return rows[0].get("qid")
        return None

    def add(self, title: str, qid: str) -> None:
        """Add or update a QID for a title.

        Args:
            title: MDWiki page title
            qid: Wikidata QID
        """
        self.db.execute_query_safe(
            """
            INSERT INTO qids (title, qid)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE qid = VALUES(qid)
            """,
            (title, qid),
        )


__all__ = [
    "QidsDB",
    "ensure_qids_table",
    "qids_table_creation_sql",
]
