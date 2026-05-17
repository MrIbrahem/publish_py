"""
SQLAlchemy-based service for managing assessments.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...models import AssessmentRecord
from ....shared.core.extensions import db

logger = logging.getLogger(__name__)


def list_assessments() -> List[AssessmentRecord]:
    """Return all assessment records."""
    orm_objs = db.session.query(AssessmentRecord).order_by(AssessmentRecord.id.asc()).all()
    return orm_objs


def get_assessment(assessment_id: int) -> AssessmentRecord | None:
    """Get an assessment record by ID."""
    orm_obj = db.session.query(AssessmentRecord).filter(AssessmentRecord.id == assessment_id).first()
    if not orm_obj:
        logger.warning(f"Assessment record with ID {assessment_id} not found")
        return None
    return orm_obj


def get_assessment_by_title(title: str) -> AssessmentRecord | None:
    """Get an assessment record by title."""
    orm_obj = db.session.query(AssessmentRecord).filter(AssessmentRecord.title == title).first()
    if not orm_obj:
        return None
    return orm_obj


def add_assessment(title: str, importance: str | None = None) -> AssessmentRecord:
    """Add a new assessment record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    orm_obj = AssessmentRecord(title=title, importance=importance)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Assessment for '{title}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def add_or_update_assessment(title: str, importance: str | None = None) -> AssessmentRecord:
    """Add or update an assessment record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    orm_obj = db.session.query(AssessmentRecord).filter(AssessmentRecord.title == title).first()
    if orm_obj:
        orm_obj.importance = importance
    else:
        orm_obj = AssessmentRecord(title=title, importance=importance)
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_assessment(assessment_id: int, **kwargs) -> AssessmentRecord:
    """Update an assessment record."""
    orm_obj = db.session.query(AssessmentRecord).filter(AssessmentRecord.id == assessment_id).first()
    if not orm_obj:
        raise ValueError(f"Assessment record with ID {assessment_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_assessment(assessment_id: int) -> AssessmentRecord:
    """Delete an assessment record by ID."""
    orm_obj = db.session.query(AssessmentRecord).filter(AssessmentRecord.id == assessment_id).first()
    if not orm_obj:
        raise ValueError(f"Assessment record with ID {assessment_id} not found")

    record = AssessmentRecord(**orm_obj.to_dict())
    db.session.delete(orm_obj)
    db.session.commit()
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
