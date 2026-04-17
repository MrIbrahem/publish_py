"""
SQLAlchemy-based service for managing full translators.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.sqlalchemy_db.engine import get_session
from ..models.full_translator import FullTranslatorRecord
from ..sqlalchemy_models.full_translator import _FullTranslatorRecord

logger = logging.getLogger(__name__)


def list_full_translators() -> List[FullTranslatorRecord]:
    """Return all full translator records."""
    with get_session() as session:
        orm_objs = session.query(_FullTranslatorRecord).order_by(_FullTranslatorRecord.id.asc()).all()
        return [FullTranslatorRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def list_active_full_translators() -> List[FullTranslatorRecord]:
    """Return all active full translator records."""
    with get_session() as session:
        orm_objs = (
            session.query(_FullTranslatorRecord)
            .filter(_FullTranslatorRecord.active == 1)
            .order_by(_FullTranslatorRecord.id.asc())
            .all()
        )
        return [FullTranslatorRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_full_translator(translator_id: int) -> FullTranslatorRecord | None:
    """Get a full translator record by ID."""
    with get_session() as session:
        orm_obj = session.query(_FullTranslatorRecord).filter(_FullTranslatorRecord.id == translator_id).first()
        if not orm_obj:
            logger.warning(f"Full translator record with ID {translator_id} not found")
            return None
        return FullTranslatorRecord(**orm_obj.to_dict())


def get_full_translator_by_user(user: str) -> FullTranslatorRecord | None:
    """Get a full translator record by username."""
    with get_session() as session:
        orm_obj = session.query(_FullTranslatorRecord).filter(_FullTranslatorRecord.user == user).first()
        if not orm_obj:
            return None
        return FullTranslatorRecord(**orm_obj.to_dict())


def add_full_translator(user: str, active: int = 1) -> FullTranslatorRecord:
    """Add a new full translator record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    with get_session() as session:
        orm_obj = _FullTranslatorRecord(user=user, active=active)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Full translator '{user}' already exists") from None

        session.refresh(orm_obj)
        return FullTranslatorRecord(**orm_obj.to_dict())


def add_or_update_full_translator(user: str, active: int = 1) -> FullTranslatorRecord:
    """Add or update a full translator record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    with get_session() as session:
        orm_obj = session.query(_FullTranslatorRecord).filter(_FullTranslatorRecord.user == user).first()
        if orm_obj:
            orm_obj.active = active
        else:
            orm_obj = _FullTranslatorRecord(user=user, active=active)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return FullTranslatorRecord(**orm_obj.to_dict())


def update_full_translator(translator_id: int, **kwargs) -> FullTranslatorRecord:
    """Update a full translator record."""
    with get_session() as session:
        orm_obj = session.query(_FullTranslatorRecord).filter(_FullTranslatorRecord.id == translator_id).first()
        if not orm_obj:
            raise ValueError(f"Full translator record with ID {translator_id} not found")

        if not kwargs:
            return FullTranslatorRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return FullTranslatorRecord(**orm_obj.to_dict())


def delete_full_translator(translator_id: int) -> FullTranslatorRecord:
    """Delete a full translator record by ID."""
    with get_session() as session:
        orm_obj = session.query(_FullTranslatorRecord).filter(_FullTranslatorRecord.id == translator_id).first()
        if not orm_obj:
            raise ValueError(f"Full translator record with ID {translator_id} not found")

        record = FullTranslatorRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def is_full_translator(user: str) -> bool:
    """Check if a user is a full translator."""
    record = get_full_translator_by_user(user)
    return record is not None and record.active == 1


__all__ = [
    "list_full_translators",
    "list_active_full_translators",
    "get_full_translator",
    "get_full_translator_by_user",
    "add_full_translator",
    "add_or_update_full_translator",
    "update_full_translator",
    "delete_full_translator",
    "is_full_translator",
]
