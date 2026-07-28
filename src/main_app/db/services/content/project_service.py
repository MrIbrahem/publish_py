"""
SQLAlchemy-based service for managing projects.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import ProjectRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class ProjectService(CRUDService[ProjectRecord]):
    model = ProjectRecord

    def __init__(self):
        super().__init__(db.session, ProjectRecord)

    def list_projects(self) -> list[ProjectRecord]:
        """Return all project records."""
        return list(
            self.list(
                order_by=[ProjectRecord.g_title.asc()],
            )
        )

    def get_project(self, project_id: int) -> ProjectRecord | None:
        """Get a project record by ID."""
        orm_obj = self.get(project_id)
        if not orm_obj:
            logger.warning(f"Project record with ID {project_id} not found")
            return None
        return orm_obj

    def get_project_by_title(self, title: str) -> ProjectRecord | None:
        """Get a project record by title."""
        return self.get_by(g_title=title)

    def add_project(self, g_title: str) -> ProjectRecord:
        """Add a new project record."""
        g_title = g_title.strip()
        if not g_title:
            raise ValueError("Project title is required")

        try:
            return self.create(g_title=g_title)
        except IntegrityError:
            raise ValueError(f"Project '{g_title}' already exists") from None

    def update_project(self, project_id: int, **kwargs) -> ProjectRecord:
        """Update a project record."""
        # Apply the same title validation/normalization as add_project()
        normalized_kwargs = {}
        for key, value in kwargs.items():
            if key in ("title", "g_title"):
                if not isinstance(value, str):
                    raise ValueError("Project title must be a string")
                stripped = value.strip()
                if not stripped:
                    raise ValueError("Project title is required")
                normalized_kwargs[key] = stripped
            else:
                normalized_kwargs[key] = value

        return self.update_or_404(project_id, **normalized_kwargs)

    def update_project_title(self, project_id: int, g_title: str) -> ProjectRecord:
        """Update a project record."""
        g_title = g_title.strip() if isinstance(g_title, str) else g_title
        if not g_title:
            raise ValueError("Project title is required")

        record = self.get_record_by_id(project_id)
        if record is None:
            raise ValueError(f"Project record with ID {project_id} not found")
        try:
            data = {"g_title": g_title}
            return self.update(record, **data)
        except ValueError as exc:
            raise ValueError(f"Project record with ID {project_id} not found") from exc


_crud = ProjectService()
list_projects = _crud.list_projects
get_project = _crud.get_project
get_project_by_title = _crud.get_project_by_title
add_project = _crud.add_project
update_project = _crud.update_project
update_project_title = _crud.update_project_title

__all__ = [
    "list_projects",
    "get_project",
    "get_project_by_title",
    "add_project",
    "update_project",
    "update_project_title",
]
