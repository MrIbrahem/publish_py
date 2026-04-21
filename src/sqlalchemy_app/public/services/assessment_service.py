"""
SQLAlchemy-based service for managing assessments.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...db_models import AssessmentRecord
from ...shared.engine import get_session
from ...sqlalchemy_models import _AssessmentRecord

logger = logging.getLogger(__name__)


def list_assessments() -> List[AssessmentRecord]:
    """Return all assessment records."""
    with get_session() as session:
        orm_objs = session.query(_AssessmentRecord).order_by(_AssessmentRecord.id.asc()).all()
        return [AssessmentRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_assessment(assessment_id: int) -> AssessmentRecord | None:
    """Get an assessment record by ID."""
    with get_session() as session:
        orm_obj = session.query(_AssessmentRecord).filter(_AssessmentRecord.id == assessment_id).first()
        if not orm_obj:
            logger.warning(f"Assessment record with ID {assessment_id} not found")
            return None
        return AssessmentRecord(**orm_obj.to_dict())


def get_assessment_by_title(title: str) -> AssessmentRecord | None:
    """Get an assessment record by title."""
    with get_session() as session:
        orm_obj = session.query(_AssessmentRecord).filter(_AssessmentRecord.title == title).first()
        if not orm_obj:
            return None
        return AssessmentRecord(**orm_obj.to_dict())


def add_assessment(title: str, importance: str | None = None) -> AssessmentRecord:
    """Add a new assessment record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = _AssessmentRecord(title=title, importance=importance)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Assessment for '{title}' already exists") from None

        session.refresh(orm_obj)
        return AssessmentRecord(**orm_obj.to_dict())


def add_or_update_assessment(title: str, importance: str | None = None) -> AssessmentRecord:
    """Add or update an assessment record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = session.query(_AssessmentRecord).filter(_AssessmentRecord.title == title).first()
        if orm_obj:
            orm_obj.importance = importance
        else:
            orm_obj = _AssessmentRecord(title=title, importance=importance)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return AssessmentRecord(**orm_obj.to_dict())


def update_assessment(assessment_id: int, **kwargs) -> AssessmentRecord:
    """Update an assessment record."""
    with get_session() as session:
        orm_obj = session.query(_AssessmentRecord).filter(_AssessmentRecord.id == assessment_id).first()
        if not orm_obj:
            raise ValueError(f"Assessment record with ID {assessment_id} not found")

        if not kwargs:
            return AssessmentRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return AssessmentRecord(**orm_obj.to_dict())


def delete_assessment(assessment_id: int) -> AssessmentRecord:
    """Delete an assessment record by ID."""
    with get_session() as session:
        orm_obj = session.query(_AssessmentRecord).filter(_AssessmentRecord.id == assessment_id).first()
        if not orm_obj:
            raise ValueError(f"Assessment record with ID {assessment_id} not found")

        record = AssessmentRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


__all__ = [
    "list_assessments",
    "get_assessment",
    "get_assessment_by_title",
    "add_assessment",
    "add_or_update_assessment",
    "update_assessment",
    "delete_assessment",
]
