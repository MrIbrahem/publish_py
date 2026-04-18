"""Utilities for managing assessments."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ..db.db_assessments import AssessmentsDB
from ..models import AssessmentRecord

logger = logging.getLogger(__name__)

_ASSESSMENTS_STORE: AssessmentsDB | None = None


from ....config import has_db_config


def get_assessments_db() -> AssessmentsDB:
    global _ASSESSMENTS_STORE

    if _ASSESSMENTS_STORE is None:
        if not has_db_config():
            raise RuntimeError("AssessmentsDB requires database configuration; no fallback store is available.")

        try:
            _ASSESSMENTS_STORE = AssessmentsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL AssessmentsDB")
            raise RuntimeError("Unable to initialize AssessmentsDB") from exc

    return _ASSESSMENTS_STORE


def list_assessments() -> List[AssessmentRecord]:
    """Return all assessment records."""
    store = get_assessments_db()
    return store.list()


def get_assessment(assessment_id: int) -> AssessmentRecord | None:
    """Get an assessment record by ID."""
    store = get_assessments_db()
    return store.fetch_by_id(assessment_id)


def get_assessment_by_title(title: str) -> AssessmentRecord | None:
    """Get an assessment record by title."""
    store = get_assessments_db()
    return store.fetch_by_title(title)


def add_assessment(title: str, importance: str | None = None) -> AssessmentRecord:
    """Add a new assessment record."""
    store = get_assessments_db()
    return store.add(title, importance)


def add_or_update_assessment(title: str, importance: str | None = None) -> AssessmentRecord:
    """Add or update an assessment record."""
    store = get_assessments_db()
    return store.add_or_update(title, importance)


def update_assessment(assessment_id: int, **kwargs) -> AssessmentRecord:
    """Update an assessment record."""
    store = get_assessments_db()
    return store.update(assessment_id, **kwargs)


def delete_assessment(assessment_id: int) -> AssessmentRecord:
    """Delete an assessment record by ID."""
    store = get_assessments_db()
    return store.delete(assessment_id)


__all__ = [
    "get_assessments_db",
    "list_assessments",
    "get_assessment",
    "get_assessment_by_title",
    "add_assessment",
    "add_or_update_assessment",
    "update_assessment",
    "delete_assessment",
]
