"""
SQLAlchemy-based service for managing words.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ..engine import get_session
from ...sqlalchemy_models import WordRecord

logger = logging.getLogger(__name__)


def list_words() -> List[WordRecord]:
    """Return all word records."""
    with get_session() as session:
        orm_objs = session.query(WordRecord).order_by(WordRecord.w_id.asc()).all()
        return orm_objs


def get_word(word_id: int) -> WordRecord | None:
    """Get a word record by ID."""
    with get_session() as session:
        orm_obj = session.query(WordRecord).filter(WordRecord.w_id == word_id).first()
        if not orm_obj:
            logger.warning(f"Word record with ID {word_id} not found")
            return None
        return orm_obj


def get_word_by_title(title: str) -> WordRecord | None:
    """Get a word record by title."""
    with get_session() as session:
        orm_obj = session.query(WordRecord).filter(WordRecord.w_title == title).first()
        if not orm_obj:
            return None
        return orm_obj


def add_word(
    w_title: str,
    w_lead_words: int | None = None,
    w_all_words: int | None = None,
) -> WordRecord:
    """Add a new word record."""
    w_title = w_title.strip()
    if not w_title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = WordRecord(w_title=w_title, w_lead_words=w_lead_words, w_all_words=w_all_words)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Word count for '{w_title}' already exists") from None

        session.refresh(orm_obj)
        return orm_obj


def add_or_update_word(
    w_title: str,
    w_lead_words: int | None = None,
    w_all_words: int | None = None,
) -> WordRecord:
    """Add or update a word record."""
    w_title = w_title.strip()
    if not w_title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = session.query(WordRecord).filter(WordRecord.w_title == w_title).first()
        if orm_obj:
            orm_obj.w_lead_words = w_lead_words
            orm_obj.w_all_words = w_all_words
        else:
            orm_obj = WordRecord(w_title=w_title, w_lead_words=w_lead_words, w_all_words=w_all_words)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return orm_obj


def update_word(word_id: int, **kwargs) -> WordRecord:
    """Update a word record."""
    with get_session() as session:
        orm_obj = session.query(WordRecord).filter(WordRecord.w_id == word_id).first()
        if not orm_obj:
            raise ValueError(f"Word record with ID {word_id} not found")

        if not kwargs:
            return orm_obj

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return orm_obj


def delete_word(word_id: int) -> WordRecord:
    """Delete a word record by ID."""
    with get_session() as session:
        orm_obj = session.query(WordRecord).filter(WordRecord.w_id == word_id).first()
        if not orm_obj:
            raise ValueError(f"Word record with ID {word_id} not found")

        record = WordRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def get_word_counts_for_title(title: str) -> tuple[int | None, int | None]:
    """Get lead and all word counts for a title."""
    record = get_word_by_title(title)
    if record:
        return record.w_lead_words, record.w_all_words
    return None, None


__all__ = [
    "list_words",
    "get_word",
    "get_word_by_title",
    "add_word",
    "add_or_update_word",
    "update_word",
    "delete_word",
    "get_word_counts_for_title",
]
