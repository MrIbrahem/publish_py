"""
SQLAlchemy-based service for managing full translators.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import FullTranslatorRecord

logger = logging.getLogger(__name__)


def list_full_translators() -> List[FullTranslatorRecord]:
    """Return all full translator records."""
    orm_objs = db.session.query(FullTranslatorRecord).order_by(FullTranslatorRecord.id.asc()).all()
    return orm_objs


def list_active_full_translators() -> List[FullTranslatorRecord]:
    """Return all is_active full translator records."""
    orm_objs = (
        db.session.query(FullTranslatorRecord)
        .filter(FullTranslatorRecord.is_active == 1)
        .order_by(FullTranslatorRecord.id.asc())
        .all()
    )
    return orm_objs


def get_full_translator(translator_id: int) -> FullTranslatorRecord | None:
    """Get a full translator record by ID."""
    orm_obj = db.session.get(FullTranslatorRecord, translator_id)
    if not orm_obj:
        logger.warning(f"Full translator record with ID {translator_id} not found")
        return None
    return orm_obj


def get_full_translator_by_user(user: str) -> FullTranslatorRecord | None:
    """Get a full translator record by username."""
    orm_obj = db.session.query(FullTranslatorRecord).filter(FullTranslatorRecord.user == user).first()
    if not orm_obj:
        return None
    return orm_obj


def add_full_translator(user: str, is_active: int = 1) -> FullTranslatorRecord:
    """Add a new full translator record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    orm_obj = FullTranslatorRecord(user=user, is_active=is_active)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Full translator '{user}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def add_or_update_full_translator(user: str, is_active: int = 1) -> FullTranslatorRecord:
    """Add or update a full translator record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    orm_obj = db.session.query(FullTranslatorRecord).filter(FullTranslatorRecord.user == user).first()
    if orm_obj:
        orm_obj.is_active = is_active
    else:
        orm_obj = FullTranslatorRecord(user=user, is_active=is_active)
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_full_translator(translator_id: int, **kwargs) -> FullTranslatorRecord:
    """Update a full translator record."""
    orm_obj = db.session.get(FullTranslatorRecord, translator_id)
    if not orm_obj:
        raise ValueError(f"Full translator record with ID {translator_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def is_full_translator(user: str) -> bool:
    """Check if a user is a full translator."""
    record = get_full_translator_by_user(user)
    return record is not None and record.is_active == 1


__all__ = [
    "list_full_translators",
    "list_active_full_translators",
    "get_full_translator",
    "get_full_translator_by_user",
    "add_full_translator",
    "add_or_update_full_translator",
    "update_full_translator",
    "is_full_translator",
]
