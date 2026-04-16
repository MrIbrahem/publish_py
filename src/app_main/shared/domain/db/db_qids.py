"""Database handler for qids table.

Stores Wikidata QIDs for MDWiki page titles.
"""

from __future__ import annotations

import logging
from typing import Any, List

from ....config import DbConfig
from ...core.db_driver import Database
from ..models import QidRecord

logger = logging.getLogger(__name__)


class QidsDB:
    """MySQL-backed database handler for qids table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> QidRecord:
        return QidRecord(**row)

    def fetch_by_id(self, qid_id: int) -> QidRecord | None:
        """Get a QID record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT id, title, qid, add_date FROM qids WHERE id = %s",
            (qid_id,),
        )
        if not rows:
            logger.warning(f"QID record with ID {qid_id} not found")
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[QidRecord]:
        rows = self.db.fetch_query_safe("SELECT id, title, qid, add_date FROM qids ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def fetch_by_title(self, title: str) -> QidRecord | None:
        """Get the QID record for a specific page title."""
        rows = self.db.fetch_query_safe(
            "SELECT id, title, qid, add_date FROM qids WHERE title = %s",
            (title,),
        )
        if not rows:
            logger.warning(f"QID for title {title} not found")
            return None

        return self._row_to_record(rows[0])

    def fetch_by_qid(self, qid: str) -> QidRecord | None:
        """Get the QID record for a specific QID."""
        rows = self.db.fetch_query_safe(
            "SELECT id, title, qid, add_date FROM qids WHERE qid = %s",
            (qid,),
        )
        if not rows:
            logger.warning(f"Record with QID {qid} not found")
            return None

        return self._row_to_record(rows[0])

    def delete(self, qid_id: int) -> None:
        """Delete a QID record by ID."""
        record = self.fetch_by_id(qid_id)
        if not record:
            raise ValueError(f"QID record with ID {qid_id} not found")

        self.db.execute_query_safe("DELETE FROM qids WHERE id = %s", (qid_id,))

    def add(self, title: str, qid: str) -> QidRecord | None:
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
        return self.fetch_by_title(title)

    def update(self, qid_id: int, title: str, qid: str) -> QidRecord:
        """Update a QID record."""
        record = self.fetch_by_id(qid_id)
        if not record:
            raise ValueError(f"QID record with ID {qid_id} not found")

        self.db.execute_query_safe(
            "UPDATE qids SET title = %s, qid = %s WHERE id = %s",
            (title, qid, qid_id),
        )
        updated = self.fetch_by_id(qid_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated QID record with ID {qid_id}")
        return updated


__all__ = [
    "QidsDB",
]
