"""
SQLAlchemy-based service for managing translate types.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...db.models import TranslateTypeRecord
from ..core.extensions import db

logger = logging.getLogger(__name__)


def list_translate_types() -> List[TranslateTypeRecord]:
    """Return all translate_type records."""
    orm_objs = db.session.query(TranslateTypeRecord).order_by(TranslateTypeRecord.tt_id.asc()).all()
    return orm_objs


def list_lead_enabled_types() -> List[TranslateTypeRecord]:
    """Return translate_type records with lead enabled."""
    orm_objs = (
        db.session.query(TranslateTypeRecord)
        .filter(TranslateTypeRecord.tt_lead == 1)
        .order_by(TranslateTypeRecord.tt_id.asc())
        .all()
    )
    return orm_objs


def list_full_enabled_types() -> List[TranslateTypeRecord]:
    """Return translate_type records with full enabled."""
    orm_objs = (
        db.session.query(TranslateTypeRecord)
        .filter(TranslateTypeRecord.tt_full == 1)
        .order_by(TranslateTypeRecord.tt_id.asc())
        .all()
    )
    return orm_objs


def get_translate_type(tt_id: int) -> TranslateTypeRecord | None:
    """Get a translate_type record by ID."""
    orm_obj = db.session.query(TranslateTypeRecord).filter(TranslateTypeRecord.tt_id == tt_id).first()
    if not orm_obj:
        logger.warning(f"TranslateType record with ID {tt_id} not found")
        return None
    return orm_obj


def get_translate_type_by_title(title: str) -> TranslateTypeRecord | None:
    """Get a translate_type record by title."""
    orm_obj = db.session.query(TranslateTypeRecord).filter(TranslateTypeRecord.tt_title == title).first()
    if not orm_obj:
        return None
    return orm_obj


def add_translate_type(
    tt_title: str,
    tt_lead: int = 1,
    tt_full: int = 0,
) -> TranslateTypeRecord:
    """Add a new translate_type record."""
    tt_title = tt_title.strip()
    if not tt_title:
        raise ValueError("Title is required")

    orm_obj = TranslateTypeRecord(tt_title=tt_title, tt_lead=tt_lead, tt_full=tt_full)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Translate type '{tt_title}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def add_or_update_translate_type(
    tt_title: str,
    tt_lead: int = 1,
    tt_full: int = 0,
) -> TranslateTypeRecord:
    """Add or update a translate_type record."""
    tt_title = tt_title.strip()
    if not tt_title:
        raise ValueError("Title is required")

    orm_obj = db.session.query(TranslateTypeRecord).filter(TranslateTypeRecord.tt_title == tt_title).first()
    if orm_obj:
        orm_obj.tt_lead = tt_lead
        orm_obj.tt_full = tt_full
    else:
        orm_obj = TranslateTypeRecord(tt_title=tt_title, tt_lead=tt_lead, tt_full=tt_full)
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_translate_type(tt_id: int, **kwargs) -> TranslateTypeRecord:
    """Update a translate_type record."""
    orm_obj = db.session.query(TranslateTypeRecord).filter(TranslateTypeRecord.tt_id == tt_id).first()
    if not orm_obj:
        raise ValueError(f"TranslateType record with ID {tt_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_translate_type(tt_id: int) -> TranslateTypeRecord:
    """Delete a translate_type record by ID."""
    orm_obj = db.session.query(TranslateTypeRecord).filter(TranslateTypeRecord.tt_id == tt_id).first()
    if not orm_obj:
        raise ValueError(f"TranslateType record with ID {tt_id} not found")

    record = TranslateTypeRecord(**orm_obj.to_dict())
    db.session.delete(orm_obj)
    db.session.commit()
    return record


def can_translate_lead(title: str) -> bool:
    """Check if a title can be translated as lead."""
    record = get_translate_type_by_title(title)
    return record.tt_lead == 1 if record else True


def can_translate_full(title: str) -> bool:
    """Check if a title can be translated as full."""
    record = get_translate_type_by_title(title)
    return record.tt_full == 1 if record else False


__all__ = [
    "list_translate_types",
    "list_lead_enabled_types",
    "list_full_enabled_types",
    "get_translate_type",
    "get_translate_type_by_title",
    "add_translate_type",
    "add_or_update_translate_type",
    "update_translate_type",
    "delete_translate_type",
    "can_translate_lead",
    "can_translate_full",
]
