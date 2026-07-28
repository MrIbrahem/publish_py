"""
SQLAlchemy-based service for managing in-process translations.
"""

from __future__ import annotations

import logging

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import InProcessRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class InProcessService(CRUDService[InProcessRecord, int]):
    model = InProcessRecord


in_process_crud = InProcessService(db.session)


def list_in_process() -> list[InProcessRecord]:
    """Return all in_process records."""
    return list(
        in_process_crud.list(
            order_by=[InProcessRecord.id.asc()],
        )
    )


def list_in_process_by_user(user: str) -> list[InProcessRecord]:
    """Return in_process records for a specific user."""
    return list(
        in_process_crud.list(
            filters={"user": user},
            order_by=[InProcessRecord.id.asc()],
        )
    )


def list_in_process_by_lang(lang: str) -> list[InProcessRecord]:
    """Return in_process records for a specific language."""
    return list(
        in_process_crud.list(
            filters={"lang": lang},
            order_by=[InProcessRecord.id.asc()],
        )
    )


def get_in_process(process_id: int) -> InProcessRecord | None:
    """Get an in_process record by ID."""
    orm_obj = in_process_crud.get(process_id)
    if not orm_obj:
        logger.warning(f"In-process record with ID {process_id} not found")
        return None
    return orm_obj


def get_in_process_by_title_user_lang(title: str, user: str, lang: str) -> InProcessRecord | None:
    """Get an in_process record by title, user, and language."""
    return in_process_crud.get_by(title=title, user=user, lang=lang)


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

    try:
        return in_process_crud.create(
            title=title,
            user=user,
            lang=lang,
            cat=cat,
            translate_type=translate_type,
            word=word,
            add_date=func.now(),
        )
    except IntegrityError:
        raise ValueError(f"In-process record for '{title}' by '{user}' in '{lang}' already exists") from None


def update_in_process(process_id: int, **kwargs) -> InProcessRecord:
    """Update an in_process record."""
    if not kwargs:
        orm_obj = in_process_crud.get(process_id)
        if not orm_obj:
            raise ValueError(f"In-process record with ID {process_id} not found")
        return orm_obj

    try:
        return in_process_crud.update(process_id, **kwargs)
    except ValueError as exc:
        raise ValueError(f"In-process record with ID {process_id} not found") from exc


def delete_in_process_by_title_user_lang(title: str, user: str, lang: str) -> bool:
    """Delete an in_process record by title, user, and language."""
    record = in_process_crud.get_by(title=title, user=user, lang=lang)
    if not record:
        return False
    return in_process_crud.delete(record.id)


def is_in_process(title: str, user: str, lang: str) -> bool:
    """Check if a translation is in process."""
    record = get_in_process_by_title_user_lang(title, user, lang)
    return record is not None


def get_in_process_counts_by_user() -> list[dict]:
    """Get count of in-process translations per user, sorted by count descending."""
    results = (
        in_process_crud.session.query(
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
    "delete_in_process_by_title_user_lang",
    "is_in_process",
    "get_in_process_counts_by_user",
]
