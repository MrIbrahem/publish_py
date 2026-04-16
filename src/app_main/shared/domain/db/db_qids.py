"""
Database handler for qids table.

Stores Wikidata QIDs for MDWiki page titles.
"""

from __future__ import annotations

import logging
from typing import Any, List

from src.app_main.shared.domain.models import QidRecord

from ....config import DbConfig
from ...core.db_driver import Database

logger = logging.getLogger(__name__)


class QidsDB:
    """MySQL-backed database handler for qids table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> QidRecord:
        return QidRecord(**row)

    def list(self) -> List[QidRecord]:
        rows = self.db.fetch_query_safe(
            "SELECT id, title, qid, add_date FROM qids ORDER BY id ASC"
        )
        return [self._row_to_record(row) for row in rows]

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
            ON DUPLICATE KEY UPDATE
                qid = VALUES(qid)
            """,
            (title, qid),
        )


__all__ = [
    "QidsDB",
]
