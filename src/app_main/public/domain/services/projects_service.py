"""Utilities for managing projects."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ...shared.domain.services.db_service import has_db_config
from ..db.db_projects import ProjectsDB
from ..models.project import ProjectRecord

logger = logging.getLogger(__name__)

_PROJECTS_STORE: ProjectsDB | None = None


def get_projects_db() -> ProjectsDB:
    global _PROJECTS_STORE

    if _PROJECTS_STORE is None:
        if not has_db_config():
            raise RuntimeError("ProjectsDB requires database configuration; no fallback store is available.")

        try:
            _PROJECTS_STORE = ProjectsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL ProjectsDB")
            raise RuntimeError("Unable to initialize ProjectsDB") from exc

    return _PROJECTS_STORE


def list_projects() -> List[ProjectRecord]:
    """Return all project records."""
    store = get_projects_db()
    return store.list()


def get_project(project_id: int) -> ProjectRecord | None:
    """Get a project record by ID."""
    store = get_projects_db()
    return store.fetch_by_id(project_id)


def get_project_by_title(title: str) -> ProjectRecord | None:
    """Get a project record by title."""
    store = get_projects_db()
    return store.fetch_by_title(title)


def add_project(g_title: str) -> ProjectRecord:
    """Add a new project record."""
    store = get_projects_db()
    return store.add(g_title)


def add_or_update_project(g_title: str) -> ProjectRecord:
    """Add or update a project record."""
    store = get_projects_db()
    return store.add_or_update(g_title)


def update_project(project_id: int, **kwargs) -> ProjectRecord:
    """Update a project record."""
    store = get_projects_db()
    return store.update(project_id, **kwargs)


def delete_project(project_id: int) -> ProjectRecord:
    """Delete a project record by ID."""
    store = get_projects_db()
    return store.delete(project_id)


__all__ = [
    "get_projects_db",
    "list_projects",
    "get_project",
    "get_project_by_title",
    "add_project",
    "add_or_update_project",
    "update_project",
    "delete_project",
]
