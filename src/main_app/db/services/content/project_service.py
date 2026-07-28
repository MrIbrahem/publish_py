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


class ProjectService(CRUDService[ProjectRecord, int]):
    model = ProjectRecord


project_crud = ProjectService(db.session)


def list_projects() -> list[ProjectRecord]:
    """Return all project records."""
    return list(
        project_crud.list(
            order_by=[ProjectRecord.g_title.asc()],
        )
    )


def get_project(project_id: int) -> ProjectRecord | None:
    """Get a project record by ID."""
    orm_obj = project_crud.get(project_id)
    if not orm_obj:
        logger.warning(f"Project record with ID {project_id} not found")
        return None
    return orm_obj


def get_project_by_title(title: str) -> ProjectRecord | None:
    """Get a project record by title."""
    return project_crud.get_by(g_title=title)


def add_project(g_title: str) -> ProjectRecord:
    """Add a new project record."""
    g_title = g_title.strip()
    if not g_title:
        raise ValueError("Project title is required")

    try:
        return project_crud.create(g_title=g_title)
    except IntegrityError:
        raise ValueError(f"Project '{g_title}' already exists") from None


def update_project(project_id: int, **kwargs) -> ProjectRecord:
    """Update a project record."""
    if not kwargs:
        orm_obj = project_crud.get(project_id)
        if not orm_obj:
            raise ValueError(f"Project record with ID {project_id} not found")
        return orm_obj

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

    try:
        return project_crud.update(project_id, **normalized_kwargs)
    except ValueError as exc:
        raise ValueError(f"Project record with ID {project_id} not found") from exc


def update_project_title(project_id: int, g_title: str) -> ProjectRecord:
    """Update a project record."""
    g_title = g_title.strip() if isinstance(g_title, str) else g_title
    if not g_title:
        raise ValueError("Project title is required")

    try:
        return project_crud.update(project_id, g_title=g_title)
    except ValueError as exc:
        raise ValueError(f"Project record with ID {project_id} not found") from exc


__all__ = [
    "list_projects",
    "get_project",
    "get_project_by_title",
    "add_project",
    "update_project",
    "update_project_title",
]
