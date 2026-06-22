"""
SQLAlchemy-based service for managing pages_users and page targets.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, List

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import UserPageRecord

logger = logging.getLogger(__name__)


def list_user_pages() -> List[UserPageRecord]:
    """Return all pages_users."""
    orm_objs = db.session.query(UserPageRecord).order_by(UserPageRecord.id.asc()).all()
    return orm_objs


def list_translated(lang: str = "All", limit: int = 500, offset: int = 0) -> List[UserPageRecord]:
    """Return translated user pages (target not empty) optionally filtered by language."""
    query = db.session.query(UserPageRecord).filter(UserPageRecord.target.isnot(None), UserPageRecord.target != "")
    if lang and lang != "All":
        query = query.filter(UserPageRecord.lang == lang)
    return query.order_by(UserPageRecord.id.desc()).limit(limit).offset(offset).all()


def count_translated(lang: str = "All") -> int:
    """Return total count of translated user pages, optionally filtered by language."""
    query = db.session.query(func.count(UserPageRecord.id)).filter(
        UserPageRecord.target.isnot(None), UserPageRecord.target != ""
    )
    if lang and lang != "All":
        query = query.filter(UserPageRecord.lang == lang)
    return int(query.scalar() or 0)


def get_by_id(page_id: int) -> UserPageRecord | None:
    """Return a single user page row by id, or None when missing."""
    return db.session.get(UserPageRecord, page_id)


def add_user_page(
    sourcetitle: str,
    translate_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    mdwiki_revid: int | None = None,
    word: int = 0,
) -> UserPageRecord:
    """Insert a page target record."""
    if not sourcetitle:
        raise ValueError("Title is required")
    orm_obj = UserPageRecord(
        title=sourcetitle,
        word=word,
        translate_type=translate_type,
        cat=cat,
        lang=lang,
        user=user,
        pupdate=func.current_date(),
        target=target,
        mdwiki_revid=mdwiki_revid,
    )
    db.session.add(orm_obj)
    try:
        db.session.commit()
        db.session.refresh(orm_obj)
        return orm_obj
    except IntegrityError as e:
        logger.error(f"Failed to add page (integrity error): {e}")
        db.session.rollback()
        raise ValueError(f"Page with title '{sourcetitle}' already exists") from e
    except Exception as e:
        logger.error(f"Failed to add page: {e}")
        db.session.rollback()
        raise


def insert_user_page_target(
    sourcetitle: str,
    translate_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    mdwiki_revid: int | None = None,
    word: int = 0,
) -> bool:
    """Insert a user page target record and return success status."""
    try:
        add_user_page(
            sourcetitle=sourcetitle,
            translate_type=translate_type,
            cat=cat,
            lang=lang,
            user=user,
            target=target,
            mdwiki_revid=mdwiki_revid,
            word=word,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to insert user page target: {e}")
        return False


def update_user_page(
    page_id: int,
    title: str,
    target: str,
    **kwargs: dict[str, Any],
) -> UserPageRecord:
    """Update page."""
    orm_obj = db.session.get(UserPageRecord, page_id)
    if not orm_obj:
        raise LookupError(f"Page id {page_id} was not found")

    orm_obj.title = title
    orm_obj.target = target

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    try:
        db.session.commit()
        db.session.refresh(orm_obj)
    except Exception:
        logger.exception("Failed to update user page")
        db.session.rollback()
        raise
    return orm_obj


def set_user_page_target(
    record: UserPageRecord,
    target: str,
) -> bool:
    """ """
    record.target = target
    record.pupdate = datetime.now().strftime("%Y-%m-%d")

    try:
        db.session.commit()
    except Exception:
        logger.exception("Failed to update page target")
        db.session.rollback()
        return False

    return True


def find_user_page_record(
    title: str,
    lang: str,
    user: str,
) -> UserPageRecord | None:
    """
    Check if record exists
    """

    # Check existence
    orm_obj = (
        db.session.query(UserPageRecord)
        .filter(
            UserPageRecord.title == title,
            UserPageRecord.lang == lang,
            UserPageRecord.user == user,
        )
        .first()
    )
    return orm_obj


__all__ = [
    "set_user_page_target",
    "find_user_page_record",
    "list_user_pages",
    "list_translated",
    "count_translated",
    "get_by_id",
    "add_user_page",
    "update_user_page",
    "insert_user_page_target",
]
