"""
SQLAlchemy-based service for managing projects.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...sqlalchemy_models import ProjectRecord
from ..core.extensions import db

logger = logging.getLogger(__name__)


def list_projects() -> List[ProjectRecord]:
    """Return all project records."""
    orm_objs = db.session.query(ProjectRecord).order_by(ProjectRecord.g_id.asc()).all()
    return orm_objs


def get_project(project_id: int) -> ProjectRecord | None:
    """Get a project record by ID."""
    orm_obj = db.session.query(ProjectRecord).filter(ProjectRecord.g_id == project_id).first()
    if not orm_obj:
        logger.warning(f"Project record with ID {project_id} not found")
        return None
    return orm_obj


def get_project_by_title(title: str) -> ProjectRecord | None:
    """Get a project record by title."""
    orm_obj = db.session.query(ProjectRecord).filter(ProjectRecord.g_title == title).first()
    if not orm_obj:
        return None
    return orm_obj


def add_project(g_title: str) -> ProjectRecord:
    """Add a new project record."""
    g_title = g_title.strip()
    if not g_title:
        raise ValueError("Project title is required")

    orm_obj = ProjectRecord(g_title=g_title)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Project '{g_title}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def update_project(project_id: int, **kwargs) -> ProjectRecord:
    """Update a project record."""
    orm_obj = db.session.query(ProjectRecord).filter(ProjectRecord.g_id == project_id).first()
    if not orm_obj:
        raise ValueError(f"Project record with ID {project_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_project_title(project_id: int, g_title: str) -> ProjectRecord:
    """Update a project record."""
    orm_obj = db.session.query(ProjectRecord).filter(ProjectRecord.g_id == project_id).first()
    if not orm_obj:
        raise ValueError(f"Project record with ID {project_id} not found")

    orm_obj.g_title = g_title

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_project(project_id: int) -> ProjectRecord:
    """Delete a project record by ID."""
    orm_obj = db.session.query(ProjectRecord).filter(ProjectRecord.g_id == project_id).first()
    if not orm_obj:
        raise ValueError(f"Project record with ID {project_id} not found")

    record = ProjectRecord(**orm_obj.to_dict())
    db.session.delete(orm_obj)
    db.session.commit()
    return record


__all__ = [
    "list_projects",
    "get_project",
    "get_project_by_title",
    "add_project",
    "update_project",
    "update_project_title",
    "delete_project",
]
