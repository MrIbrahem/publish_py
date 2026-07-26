"""
SQLAlchemy-based service for managing pages_users and page targets.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import UserPageRecord
from ..base import CRUDService

logger = logging.getLogger(__name__)


class UserPagesService(CRUDService[UserPageRecord, int]):
    model = UserPageRecord


user_pages_crud = UserPagesService(db.session)


def list_user_pages() -> list[UserPageRecord]:
    """Return all pages_users."""
    return list(user_pages_crud.list(order_by=[UserPageRecord.id.asc()]))


def list_translated(lang: str = "All", limit: int = 500, offset: int = 0) -> list[UserPageRecord]:
    """Return translated user pages (target not empty) optionally filtered by language."""
    query = user_pages_crud.session.query(UserPageRecord).filter(UserPageRecord.target.isnot(None), UserPageRecord.target != "")
    if lang and lang.lower() != "all":
        query = query.filter(UserPageRecord.lang == lang)
    return query.order_by(UserPageRecord.id.desc()).limit(limit).offset(offset).all()


def count_translated(lang: str = "All") -> int:
    """Return total count of translated user pages, optionally filtered by language."""
    query = user_pages_crud.session.query(func.count(UserPageRecord.id)).filter(
        UserPageRecord.target.isnot(None), UserPageRecord.target != ""
    )
    if lang and lang.lower() != "all":
        query = query.filter(UserPageRecord.lang == lang)
    return int(query.scalar() or 0)


def get_by_id(page_id: int) -> UserPageRecord | None:
    """Return a single user page row by id, or None when missing."""
    return user_pages_crud.get(page_id)


def get_user_page_by_id(page_id: int) -> UserPageRecord | None:
    """Return a single user page row by id, or None when missing."""
    return user_pages_crud.get(page_id)


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
    try:
        return user_pages_crud.create(
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
    except IntegrityError as e:
        logger.error(f"Failed to add page (integrity error): {e}")
        raise ValueError(f"Page with title '{sourcetitle}' already exists") from e
    except Exception as e:
        logger.error(f"Failed to add page: {e}")
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
    **kwargs: Any,
) -> UserPageRecord:
    """Update page."""
    try:
        return user_pages_crud.update(page_id, title=title, target=target, **kwargs)
    except ValueError as exc:
        raise LookupError(f"Page id {page_id} was not found") from exc


def set_user_page_target(
    record: UserPageRecord,
    target: str,
) -> bool:
    """ """
    try:
        user_pages_crud.update(record.id, target=target, pupdate=datetime.now().strftime("%Y-%m-%d"))
        return True
    except Exception:
        logger.exception("Failed to update page target")
        return False


def find_user_page_record(
    title: str,
    lang: str,
    user: str,
) -> UserPageRecord | None:
    """
    Check if record exists
    """
    return user_pages_crud.get_by(title=title, lang=lang, user=user)


__all__ = [
    "set_user_page_target",
    "find_user_page_record",
    "list_user_pages",
    "list_translated",
    "count_translated",
    "get_by_id",
    "get_user_page_by_id",
    "add_user_page",
    "update_user_page",
    "insert_user_page_target",
]
