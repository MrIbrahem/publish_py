"""
SQLAlchemy-based service for managing in-process translations.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ....db_models.public_models import InProcessRecord
from ...shared.engine import get_session
from ..models import _InProcessRecord

logger = logging.getLogger(__name__)


def list_in_process() -> List[InProcessRecord]:
    """Return all in_process records."""
    with get_session() as session:
        orm_objs = session.query(_InProcessRecord).order_by(_InProcessRecord.id.asc()).all()
        return [InProcessRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def list_in_process_by_user(user: str) -> List[InProcessRecord]:
    """Return in_process records for a specific user."""
    with get_session() as session:
        orm_objs = (
            session.query(_InProcessRecord)
            .filter(_InProcessRecord.user == user)
            .order_by(_InProcessRecord.id.asc())
            .all()
        )
        return [InProcessRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def list_in_process_by_lang(lang: str) -> List[InProcessRecord]:
    """Return in_process records for a specific language."""
    with get_session() as session:
        orm_objs = (
            session.query(_InProcessRecord)
            .filter(_InProcessRecord.lang == lang)
            .order_by(_InProcessRecord.id.asc())
            .all()
        )
        return [InProcessRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_in_process(process_id: int) -> InProcessRecord | None:
    """Get an in_process record by ID."""
    with get_session() as session:
        orm_obj = session.query(_InProcessRecord).filter(_InProcessRecord.id == process_id).first()
        if not orm_obj:
            logger.warning(f"In-process record with ID {process_id} not found")
            return None
        return InProcessRecord(**orm_obj.to_dict())


def get_in_process_by_title_user_lang(title: str, user: str, lang: str) -> InProcessRecord | None:
    """Get an in_process record by title, user, and language."""
    with get_session() as session:
        orm_obj = (
            session.query(_InProcessRecord)
            .filter(_InProcessRecord.title == title)
            .filter(_InProcessRecord.user == user)
            .filter(_InProcessRecord.lang == lang)
            .first()
        )
        if not orm_obj:
            return None
        return InProcessRecord(**orm_obj.to_dict())


def add_in_process(
    title: str,
    user: str,
    lang: str,
    cat: str | None = "RTT",
    translate_type: str | None = "lead",
    word: int | None = 0,
) -> InProcessRecord:
    """Add a new in_process record."""
    title = title.strip()
    user = user.strip()
    lang = lang.strip()

    if not title:
        raise ValueError("Title is required")
    if not user:
        raise ValueError("User is required")
    if not lang:
        raise ValueError("Language is required")

    with get_session() as session:
        orm_obj = _InProcessRecord(
            title=title,
            user=user,
            lang=lang,
            cat=cat,
            translate_type=translate_type,
            word=word,
            add_date=func.now(),
        )
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"In-process record for '{title}' by '{user}' in '{lang}' already exists") from None

        session.refresh(orm_obj)
        return InProcessRecord(**orm_obj.to_dict())


def update_in_process(process_id: int, **kwargs) -> InProcessRecord:
    """Update an in_process record."""
    with get_session() as session:
        orm_obj = session.query(_InProcessRecord).filter(_InProcessRecord.id == process_id).first()
        if not orm_obj:
            raise ValueError(f"In-process record with ID {process_id} not found")

        if not kwargs:
            return InProcessRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return InProcessRecord(**orm_obj.to_dict())


def delete_in_process(process_id: int) -> InProcessRecord:
    """Delete an in_process record by ID."""
    with get_session() as session:
        orm_obj = session.query(_InProcessRecord).filter(_InProcessRecord.id == process_id).first()
        if not orm_obj:
            raise ValueError(f"In-process record with ID {process_id} not found")

        record = InProcessRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def delete_in_process_by_title_user_lang(title: str, user: str, lang: str) -> bool:
    """Delete an in_process record by title, user, and language."""
    with get_session() as session:
        result = (
            session.query(_InProcessRecord)
            .filter(_InProcessRecord.title == title)
            .filter(_InProcessRecord.user == user)
            .filter(_InProcessRecord.lang == lang)
            .delete()
        )
        session.commit()
        return result > 0


def is_in_process(title: str, user: str, lang: str) -> bool:
    """Check if a translation is in process."""
    record = get_in_process_by_title_user_lang(title, user, lang)
    return record is not None


__all__ = [
    "list_in_process",
    "list_in_process_by_user",
    "list_in_process_by_lang",
    "get_in_process",
    "get_in_process_by_title_user_lang",
    "add_in_process",
    "update_in_process",
    "delete_in_process",
    "delete_in_process_by_title_user_lang",
    "is_in_process",
]
