"""
SQLAlchemy-based service for managing pages_users and page targets.
"""

from __future__ import annotations

import logging
from typing import Any, List

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from ...domain_models import UserPageRecord
from ..engine import get_session
from ..models import _UserPageRecord

logger = logging.getLogger(__name__)


def list_user_pages() -> List[UserPageRecord]:
    """Return all pages_users."""
    with get_session() as session:
        orm_objs = session.query(_UserPageRecord).order_by(_UserPageRecord.id.asc()).all()
        return [UserPageRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def add_user_page(title: str, main_file: str) -> UserPageRecord:
    """Add a page."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = _UserPageRecord(title=title, target=main_file)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Page '{title}' already exists") from None

        session.refresh(orm_obj)
        return UserPageRecord(**orm_obj.to_dict())


def add_or_update_user_page(title: str, main_file: str) -> UserPageRecord:
    """Add or update a page."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = session.query(_UserPageRecord).filter(_UserPageRecord.title == title).first()
        if orm_obj:
            orm_obj.target = main_file
        else:
            orm_obj = _UserPageRecord(title=title, target=main_file)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return UserPageRecord(**orm_obj.to_dict())


def update_user_page(page_id: int, title: str, main_file: str) -> UserPageRecord:
    """Update page."""
    with get_session() as session:
        orm_obj = session.query(_UserPageRecord).filter(_UserPageRecord.id == page_id).first()
        if not orm_obj:
            raise LookupError(f"Page id {page_id} was not found")

        orm_obj.title = title
        orm_obj.target = main_file

        session.commit()
        session.refresh(orm_obj)
        return UserPageRecord(**orm_obj.to_dict())


def delete_user_page(page_id: int) -> UserPageRecord:
    """Delete a page."""
    with get_session() as session:
        orm_obj = session.query(_UserPageRecord).filter(_UserPageRecord.id == page_id).first()
        if not orm_obj:
            raise LookupError(f"Page id {page_id} was not found")

        record = UserPageRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def find_exists_or_update_user_page(
    title: str,
    lang: str,
    user: str,
    target: str,
) -> bool:
    """Check if record exists and update target if empty."""

    with get_session() as session:
        # Check existence
        query = text("SELECT * FROM pages_users WHERE title = :title AND lang = :lang AND user = :user")
        result = session.execute(query, {"title": title, "lang": lang, "user": user}).fetchall()

        if result:
            update_query = text(
                """
                UPDATE pages_users SET target = :target, pupdate = CURRENT_DATE
                WHERE title = :title AND lang = :lang AND user = :user AND (target = '' OR target IS NULL)
                """
            )
            session.execute(update_query, {"target": target, "title": title, "lang": lang, "user": user})
            session.commit()

        return len(result) > 0


def insert_user_page_target(
    sourcetitle: str,
    tr_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    mdwiki_revid: int | None = None,
    word: int = 0,
) -> bool | str:
    """Insert a page target record."""
    query = text(
        """
        INSERT INTO pages_users (title, word, translate_type, cat, lang, user, pupdate, target, mdwiki_revid)
        VALUES (:title, :word, :tr_type, :cat, :lang, :user, CURRENT_DATE, :target, :mdwiki_revid)
        """
    )
    params = {
        "title": sourcetitle,
        "word": word,
        "tr_type": tr_type,
        "cat": cat,
        "lang": lang,
        "user": user,
        "target": target,
        "mdwiki_revid": mdwiki_revid,
    }

    with get_session() as session:
        try:
            session.execute(query, params)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to insert page target: {e}")
            session.rollback()
            return False


__all__ = [
    "list_user_pages",
    "add_or_update_user_page",
    "add_user_page",
    "update_user_page",
    "delete_user_page",
    "find_exists_or_update_user_page",
    "insert_user_page_target",
]
