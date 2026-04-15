"""
Database handler for qids table.

Stores Wikidata QIDs for MDWiki page titles.
"""

from __future__ import annotations

import logging

from ...config import DbConfig
from ....new_app.shared.db import Database
from .sql_schema_tables import sql_tables

logger = logging.getLogger(__name__)


def ensure_qids_table(db_data: DbConfig) -> bool:
    """Create the qids table if it does not already exist.

    Args:
        db_data: Database connection configuration

    Returns:
        True if table was ensured successfully, False otherwise
    """
    try:
        db = Database(db_data)
        db.execute_query_safe(sql_tables.qids)
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
        self.db.execute_query_safe(sql_tables.qids)

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
]
