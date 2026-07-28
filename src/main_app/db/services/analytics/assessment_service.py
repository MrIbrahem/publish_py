"""
SQLAlchemy-based service for managing assessments.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import AssessmentRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class AssessmentService(CRUDService[AssessmentRecord]):
    model = AssessmentRecord

    def __init__(self):
        super().__init__(db.session, AssessmentRecord)


assessment_crud = AssessmentService()


def list_assessments() -> list[AssessmentRecord]:
    """Return all assessment records."""
    return list(
        assessment_crud.list(
            order_by=[AssessmentRecord.id.asc()],
        )
    )


def get_assessment(assessment_id: int) -> AssessmentRecord | None:
    """Get an assessment record by ID."""
    orm_obj = assessment_crud.get(assessment_id)
    if not orm_obj:
        logger.warning(f"Assessment record with ID {assessment_id} not found")
        return None
    return orm_obj


def get_assessment_by_title(title: str) -> AssessmentRecord | None:
    """Get an assessment record by title."""
    return assessment_crud.get_by(title=title)


def add_assessment(title: str, importance: str | None = None) -> AssessmentRecord:
    """Add a new assessment record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    try:
        return assessment_crud.create(title=title, importance=importance)
    except IntegrityError:
        raise ValueError(f"Assessment for '{title}' already exists") from None


def add_or_update_assessment(title: str, importance: str | None = None) -> AssessmentRecord:
    """Add or update an assessment record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    instance, is_new = assessment_crud.upsert_by(
        keys={"title": title},
        importance=importance,
    )
    return instance


def update_assessment(assessment_id: int, **kwargs) -> AssessmentRecord | None:
    """Update an assessment record."""
    return assessment_crud.update_or_404(assessment_id, **kwargs)


__all__ = [
    "list_assessments",
    "get_assessment",
    "get_assessment_by_title",
    "add_assessment",
    "add_or_update_assessment",
    "update_assessment",
]
