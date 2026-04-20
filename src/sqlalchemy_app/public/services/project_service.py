"""
SQLAlchemy-based service for managing projects.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...db_models.public_models import ProjectRecord
from ...shared.engine import get_session
from ..models import _ProjectRecord

logger = logging.getLogger(__name__)


def list_projects() -> List[ProjectRecord]:
    """Return all project records."""
    with get_session() as session:
        orm_objs = session.query(_ProjectRecord).order_by(_ProjectRecord.g_id.asc()).all()
        return [ProjectRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_project(project_id: int) -> ProjectRecord | None:
    """Get a project record by ID."""
    with get_session() as session:
        orm_obj = session.query(_ProjectRecord).filter(_ProjectRecord.g_id == project_id).first()
        if not orm_obj:
            logger.warning(f"Project record with ID {project_id} not found")
            return None
        return ProjectRecord(**orm_obj.to_dict())


def get_project_by_title(title: str) -> ProjectRecord | None:
    """Get a project record by title."""
    with get_session() as session:
        orm_obj = session.query(_ProjectRecord).filter(_ProjectRecord.g_title == title).first()
        if not orm_obj:
            return None
        return ProjectRecord(**orm_obj.to_dict())


def add_project(g_title: str) -> ProjectRecord:
    """Add a new project record."""
    g_title = g_title.strip()
    if not g_title:
        raise ValueError("Project title is required")

    with get_session() as session:
        orm_obj = _ProjectRecord(g_title=g_title)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Project '{g_title}' already exists") from None

        session.refresh(orm_obj)
        return ProjectRecord(**orm_obj.to_dict())


def update_project(project_id: int, **kwargs) -> ProjectRecord:
    """Update a project record."""
    with get_session() as session:
        orm_obj = session.query(_ProjectRecord).filter(_ProjectRecord.g_id == project_id).first()
        if not orm_obj:
            raise ValueError(f"Project record with ID {project_id} not found")

        if not kwargs:
            return ProjectRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return ProjectRecord(**orm_obj.to_dict())


def delete_project(project_id: int) -> ProjectRecord:
    """Delete a project record by ID."""
    with get_session() as session:
        orm_obj = session.query(_ProjectRecord).filter(_ProjectRecord.g_id == project_id).first()
        if not orm_obj:
            raise ValueError(f"Project record with ID {project_id} not found")

        record = ProjectRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


__all__ = [
    "list_projects",
    "get_project",
    "get_project_by_title",
    "add_project",
    "update_project",
    "delete_project",
]
