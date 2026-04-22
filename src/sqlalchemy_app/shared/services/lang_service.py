"""
SQLAlchemy-based service for managing languages.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...sqlalchemy_models import LangRecord
from ..engine import get_session

logger = logging.getLogger(__name__)


def list_langs() -> List[LangRecord]:
    """Return all language records."""
    with get_session() as session:
        orm_objs = session.query(LangRecord).order_by(LangRecord.lang_id.asc()).all()
        # return orm_objs
        return orm_objs


def get_lang(lang_id: int) -> LangRecord | None:
    """Get a language record by ID."""
    with get_session() as session:
        orm_obj = session.query(LangRecord).filter(LangRecord.lang_id == lang_id).first()
        if not orm_obj:
            logger.warning(f"Language record with ID {lang_id} not found")
            return None
        return orm_obj


def get_lang_by_code(code: str) -> LangRecord | None:
    """Get a language record by code."""
    with get_session() as session:
        orm_obj = session.query(LangRecord).filter(LangRecord.code == code).first()
        if not orm_obj:
            return None
        return orm_obj


def add_lang(code: str, autonym: str, name: str) -> LangRecord:
    """Add a new language record."""
    code = code.strip()
    if not code:
        raise ValueError("Language code is required")

    with get_session() as session:
        orm_obj = LangRecord(code=code, autonym=autonym, name=name)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Language '{code}' already exists") from None

        session.refresh(orm_obj)
        return orm_obj


def add_or_update_lang(code: str, autonym: str, name: str) -> LangRecord:
    """Add or update a language record."""
    code = code.strip()
    if not code:
        raise ValueError("Language code is required")

    with get_session() as session:
        orm_obj = session.query(LangRecord).filter(LangRecord.code == code).first()
        if orm_obj:
            orm_obj.autonym = autonym
            orm_obj.name = name
        else:
            orm_obj = LangRecord(code=code, autonym=autonym, name=name)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return orm_obj


def update_lang(lang_id: int, **kwargs) -> LangRecord:
    """Update a language record."""
    with get_session() as session:
        orm_obj = session.query(LangRecord).filter(LangRecord.lang_id == lang_id).first()
        if not orm_obj:
            raise ValueError(f"Language record with ID {lang_id} not found")

        if not kwargs:
            return orm_obj

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return orm_obj


def delete_lang(lang_id: int):
    """Delete a language record by ID."""
    with get_session() as session:
        orm_obj = session.query(LangRecord).filter(LangRecord.lang_id == lang_id).first()
        if not orm_obj:
            raise ValueError(f"Language record with ID {lang_id} not found")

        session.delete(orm_obj)
        session.commit()


__all__ = [
    "list_langs",
    "get_lang",
    "get_lang_by_code",
    "add_lang",
    "add_or_update_lang",
    "update_lang",
    "delete_lang",
]
