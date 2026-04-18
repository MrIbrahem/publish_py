"""Database handler for projects table.

Stores project records.
"""

from __future__ import annotations

import logging
from typing import Any, List

import pymysql

from ....config import DbConfig
from ....shared.core.db_driver import Database
from .....db_models.public_models import ProjectRecord

logger = logging.getLogger(__name__)


class ProjectsDB:
    """MySQL-backed database handler for projects table."""

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> ProjectRecord:
        return ProjectRecord(**row)

    def fetch_by_id(self, project_id: int) -> ProjectRecord | None:
        """Get a project record by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM projects WHERE g_id = %s",
            (project_id,),
        )
        if not rows:
            logger.warning(f"Project record with ID {project_id} not found")
            return None
        return self._row_to_record(rows[0])

    def fetch_by_title(self, title: str) -> ProjectRecord | None:
        """Get a project record by title."""
        rows = self.db.fetch_query_safe(
            "SELECT * FROM projects WHERE g_title = %s",
            (title,),
        )
        if not rows:
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[ProjectRecord]:
        """Return all project records."""
        rows = self.db.fetch_query_safe("SELECT * FROM projects ORDER BY g_id ASC")
        return [self._row_to_record(row) for row in rows]

    def add(self, g_title: str) -> ProjectRecord:
        """Add a new project record."""
        g_title = g_title.strip()
        if not g_title:
            raise ValueError("Project title is required")

        try:
            self.db.execute_query(
                "INSERT INTO projects (g_title) VALUES (%s)",
                (g_title,),
            )
        except pymysql.err.IntegrityError:
            raise ValueError(f"Project '{g_title}' already exists") from None

        record = self.fetch_by_title(g_title)
        if not record:
            raise RuntimeError(f"Failed to fetch newly created project '{g_title}'")
        return record

    def update(self, project_id: int, **kwargs) -> ProjectRecord:
        """Update a project record."""
        record = self.fetch_by_id(project_id)
        if not record:
            raise ValueError(f"Project record with ID {project_id} not found")

        if not kwargs:
            return record

        set_clause = ", ".join([f"`{col}` = %s" for col in kwargs.keys()])
        values = list(kwargs.values()) + [project_id]

        self.db.execute_query_safe(
            f"UPDATE projects SET {set_clause} WHERE g_id = %s",
            tuple(values),
        )
        updated = self.fetch_by_id(project_id)
        if not updated:
            raise RuntimeError(f"Failed to fetch updated project with ID {project_id}")
        return updated

    def delete(self, project_id: int) -> ProjectRecord:
        """Delete a project record by ID."""
        record = self.fetch_by_id(project_id)
        if not record:
            raise ValueError(f"Project record with ID {project_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM projects WHERE g_id = %s",
            (project_id,),
        )
        return record

    def add_or_update(self, g_title: str) -> ProjectRecord:
        """Add or update a project record."""
        g_title = g_title.strip()
        if not g_title:
            raise ValueError("Project title is required")

        self.db.execute_query_safe(
            """
            INSERT INTO projects (g_title)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE
                g_title = VALUES(g_title)
            """,
            (g_title,),
        )
        record = self.fetch_by_title(g_title)
        if not record:
            raise RuntimeError(f"Failed to fetch project '{g_title}' after add_or_update")
        return record


__all__ = [
    "ProjectsDB",
]
