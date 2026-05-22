"""
SQLAlchemy-based service for managing in-process translations.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import InProcessRecord

logger = logging.getLogger(__name__)


def list_in_process() -> List[InProcessRecord]:
    """Return all in_process records."""
    orm_objs = db.session.query(InProcessRecord).order_by(InProcessRecord.id.asc()).all()
    return orm_objs


def list_in_process_by_user(user: str) -> List[InProcessRecord]:
    """Return in_process records for a specific user."""
    orm_objs = (
        db.session.query(InProcessRecord).filter(InProcessRecord.user == user).order_by(InProcessRecord.id.asc()).all()
    )
    return orm_objs


def list_in_process_by_lang(lang: str) -> List[InProcessRecord]:
    """Return in_process records for a specific language."""
    orm_objs = (
        db.session.query(InProcessRecord).filter(InProcessRecord.lang == lang).order_by(InProcessRecord.id.asc()).all()
    )
    return orm_objs


def get_in_process(process_id: int) -> InProcessRecord | None:
    """Get an in_process record by ID."""
    orm_obj = db.session.get(InProcessRecord, process_id)
    if not orm_obj:
        logger.warning(f"In-process record with ID {process_id} not found")
        return None
    return orm_obj


def get_in_process_by_title_user_lang(title: str, user: str, lang: str) -> InProcessRecord | None:
    """Get an in_process record by title, user, and language."""
    orm_obj = (
        db.session.query(InProcessRecord)
        .filter(InProcessRecord.title == title)
        .filter(InProcessRecord.user == user)
        .filter(InProcessRecord.lang == lang)
        .first()
    )
    if not orm_obj:
        return None
    return orm_obj


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

    orm_obj = InProcessRecord(
        title=title,
        user=user,
        lang=lang,
        cat=cat,
        translate_type=translate_type,
        word=word,
        add_date=func.now(),
    )
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"In-process record for '{title}' by '{user}' in '{lang}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def update_in_process(process_id: int, **kwargs) -> InProcessRecord:
    """Update an in_process record."""
    orm_obj = db.session.get(InProcessRecord, process_id)
    if not orm_obj:
        raise ValueError(f"In-process record with ID {process_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_in_process(process_id: int) -> bool:
    """Delete an in_process record by ID."""
    # orm_obj = db.session.query(InProcessRecord).filter(InProcessRecord.id == process_id).first()
    orm_obj = db.session.get(InProcessRecord, process_id)
    if not orm_obj:
        raise ValueError(f"In-process record with ID {process_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(InProcessRecord, process_id)
    return deleted is None


def delete_in_process_by_title_user_lang(title: str, user: str, lang: str) -> bool:
    """Delete an in_process record by title, user, and language."""
    result = (
        db.session.query(InProcessRecord)
        .filter(InProcessRecord.title == title)
        .filter(InProcessRecord.user == user)
        .filter(InProcessRecord.lang == lang)
        .delete()
    )
    db.session.commit()
    return result > 0


def is_in_process(title: str, user: str, lang: str) -> bool:
    """Check if a translation is in process."""
    record = get_in_process_by_title_user_lang(title, user, lang)
    return record is not None


def get_in_process_counts_by_user() -> List[dict]:
    """Get count of in-process translations per user, sorted by count descending."""
    results = (
        db.session.query(
            InProcessRecord.user,
            db.func.count(InProcessRecord.id).label("article_count"),
        )
        .group_by(InProcessRecord.user)
        .order_by(db.func.count(InProcessRecord.id).desc())
        .all()
    )
    return [{"user": row.user, "article_count": row.article_count} for row in results]


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
    "get_in_process_counts_by_user",
]
