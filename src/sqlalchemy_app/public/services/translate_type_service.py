"""
SQLAlchemy-based service for managing translate types.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...db_models import TranslateTypeRecord
from ...sqlalchemy_models import _TranslateTypeRecord
from ...shared.engine import get_session

logger = logging.getLogger(__name__)


def list_translate_types() -> List[TranslateTypeRecord]:
    """Return all translate_type records."""
    with get_session() as session:
        orm_objs = session.query(_TranslateTypeRecord).order_by(_TranslateTypeRecord.tt_id.asc()).all()
        return [TranslateTypeRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def list_lead_enabled_types() -> List[TranslateTypeRecord]:
    """Return translate_type records with lead enabled."""
    with get_session() as session:
        orm_objs = (
            session.query(_TranslateTypeRecord)
            .filter(_TranslateTypeRecord.tt_lead == 1)
            .order_by(_TranslateTypeRecord.tt_id.asc())
            .all()
        )
        return [TranslateTypeRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def list_full_enabled_types() -> List[TranslateTypeRecord]:
    """Return translate_type records with full enabled."""
    with get_session() as session:
        orm_objs = (
            session.query(_TranslateTypeRecord)
            .filter(_TranslateTypeRecord.tt_full == 1)
            .order_by(_TranslateTypeRecord.tt_id.asc())
            .all()
        )
        return [TranslateTypeRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_translate_type(tt_id: int) -> TranslateTypeRecord | None:
    """Get a translate_type record by ID."""
    with get_session() as session:
        orm_obj = session.query(_TranslateTypeRecord).filter(_TranslateTypeRecord.tt_id == tt_id).first()
        if not orm_obj:
            logger.warning(f"TranslateType record with ID {tt_id} not found")
            return None
        return TranslateTypeRecord(**orm_obj.to_dict())


def get_translate_type_by_title(title: str) -> TranslateTypeRecord | None:
    """Get a translate_type record by title."""
    with get_session() as session:
        orm_obj = session.query(_TranslateTypeRecord).filter(_TranslateTypeRecord.tt_title == title).first()
        if not orm_obj:
            return None
        return TranslateTypeRecord(**orm_obj.to_dict())


def add_translate_type(
    tt_title: str,
    tt_lead: int = 1,
    tt_full: int = 0,
) -> TranslateTypeRecord:
    """Add a new translate_type record."""
    tt_title = tt_title.strip()
    if not tt_title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = _TranslateTypeRecord(tt_title=tt_title, tt_lead=tt_lead, tt_full=tt_full)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Translate type '{tt_title}' already exists") from None

        session.refresh(orm_obj)
        return TranslateTypeRecord(**orm_obj.to_dict())


def add_or_update_translate_type(
    tt_title: str,
    tt_lead: int = 1,
    tt_full: int = 0,
) -> TranslateTypeRecord:
    """Add or update a translate_type record."""
    tt_title = tt_title.strip()
    if not tt_title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = session.query(_TranslateTypeRecord).filter(_TranslateTypeRecord.tt_title == tt_title).first()
        if orm_obj:
            orm_obj.tt_lead = tt_lead
            orm_obj.tt_full = tt_full
        else:
            orm_obj = _TranslateTypeRecord(tt_title=tt_title, tt_lead=tt_lead, tt_full=tt_full)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return TranslateTypeRecord(**orm_obj.to_dict())


def update_translate_type(tt_id: int, **kwargs) -> TranslateTypeRecord:
    """Update a translate_type record."""
    with get_session() as session:
        orm_obj = session.query(_TranslateTypeRecord).filter(_TranslateTypeRecord.tt_id == tt_id).first()
        if not orm_obj:
            raise ValueError(f"TranslateType record with ID {tt_id} not found")

        if not kwargs:
            return TranslateTypeRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return TranslateTypeRecord(**orm_obj.to_dict())


def delete_translate_type(tt_id: int) -> TranslateTypeRecord:
    """Delete a translate_type record by ID."""
    with get_session() as session:
        orm_obj = session.query(_TranslateTypeRecord).filter(_TranslateTypeRecord.tt_id == tt_id).first()
        if not orm_obj:
            raise ValueError(f"TranslateType record with ID {tt_id} not found")

        record = TranslateTypeRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
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
