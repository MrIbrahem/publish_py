"""Database handler for assessments table.

Stores page assessment information.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from .....config import DbConfig
from ....shared.core.db_driver import Database
from ..models.assessment import AssessmentRecord

logger = logging.getLogger(__name__)


class AssessmentsDB:
    """MySQL-backed database handler for assessments table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> AssessmentRecord:
        return AssessmentRecord(**row)

    def fetch_by_id(self, assessment_id: int) -> AssessmentRecord | None:
        """Get an assessment record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM assessments WHERE id = %s",
            (assessment_id,),
        )
        if not rows:
            logger.warning(f"Assessment record with ID {assessment_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_title(self, title: str) -> AssessmentRecord | None:
        """Get an assessment record by title."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM assessments WHERE title = %s",
            (title,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[AssessmentRecord]:
        """Return all assessment records."""
        rows = self.db.fetch_query_safe("SELECT * FROM assessments ORDER BY id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, title: str, importance: str | None = None) -> AssessmentRecord:
        """Add a new assessment record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        try:
            self.db.execute_query(
                "INSERT INTO assessments (title, importance) VALUES (%s, %s)",
                (title, importance),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Assessment for '{title}' already exists") from None

        record = self.fetch_by_title(title)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created assessment for '{title}'")
        return record

    def update(self, assessment_id: int, **kwargs) -> AssessmentRecord:
        """Update an assessment record."""
        record = self.fetch_by_id(assessment_id)
        if not record:
            raise ValueError(f"Assessment record with ID {assessment_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [assessment_id]

        self.db.execute_query_safe(
            f"UPDATE assessments SET {set_clause} WHERE id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(assessment_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated assessment with ID {assessment_id}")
        return updated

    def delete(self, assessment_id: int) -> AssessmentRecord:
        """Delete an assessment record by ID."""
        record = self.fetch_by_id(assessment_id)
        if not record:
            raise ValueError(f"Assessment record with ID {assessment_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM assessments WHERE id = %s",
            (assessment_id,),
        )
        return record

    def add_or_update(self, title: str, importance: str | None = None) -> AssessmentRecord:
        """Add or update an assessment record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        self.db.execute_query_safe(
            """
            INSERT INTO assessments (title, importance)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                importance = VALUES(importance)
            """,
            (title, importance),
        )
        record = self.fetch_by_title(title)
        if not record:
            raise RuntimeError(f"Failed to fetch assessment for '{title}' after add_or_update")
        return record


__all__ = [
    "AssessmentsDB",
]
