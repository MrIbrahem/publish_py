"""
SQLAlchemy-based service for managing words.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import WordRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class WordService(CRUDService[WordRecord]):
    model = WordRecord

    def __init__(self):
        super().__init__(db.session, WordRecord)


word_crud = WordService()


def list_words() -> list[WordRecord]:
    """Return all word records."""
    return list(
        word_crud.list(
            order_by=[WordRecord.w_id.asc()],
        )
    )


def get_word(word_id: int) -> WordRecord | None:
    """Get a word record by ID."""
    orm_obj = word_crud.get(word_id)
    if not orm_obj:
        logger.warning(f"Word record with ID {word_id} not found")
        return None
    return orm_obj


def get_word_by_title(title: str) -> WordRecord | None:
    """Get a word record by title."""
    return word_crud.get_by(w_title=title)


def add_word(
    w_title: str,
    w_lead_words: int | None = None,
    w_all_words: int | None = None,
) -> WordRecord:
    """Add a new word record."""
    w_title = w_title.strip()
    if not w_title:
        raise ValueError("Title is required")

    try:
        return word_crud.create(w_title=w_title, w_lead_words=w_lead_words, w_all_words=w_all_words)
    except IntegrityError:
        raise ValueError(f"Word count for '{w_title}' already exists") from None


def add_or_update_word(
    w_title: str,
    w_lead_words: int | None = None,
    w_all_words: int | None = None,
) -> WordRecord:
    """Add or update a word record."""
    w_title = w_title.strip()
    if not w_title:
        raise ValueError("Title is required")

    return word_crud.upsert(
        keys={"w_title": w_title},
        w_lead_words=w_lead_words,
        w_all_words=w_all_words,
    )


def update_word(word_id: int, **kwargs) -> WordRecord:
    """Update a word record."""
    if not kwargs:
        orm_obj = word_crud.get(word_id)
        if not orm_obj:
            raise ValueError(f"Word record with ID {word_id} not found")
        return orm_obj

    try:
        return word_crud.update(word_id, **kwargs)
    except ValueError as exc:
        raise ValueError(f"Word record with ID {word_id} not found") from exc


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
    "get_word_counts_for_title",
]
