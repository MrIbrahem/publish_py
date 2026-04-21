"""
SQLAlchemy-based service for managing pages and page targets.
"""

from __future__ import annotations

import logging
from typing import Any, List

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from ...db_models import PageRecord
from ...sqlalchemy_models import _PageRecord
from ..engine import get_session

logger = logging.getLogger(__name__)


def list_pages() -> List[PageRecord]:
    """Return all pages."""
    with get_session() as session:
        orm_objs = session.query(_PageRecord).order_by(_PageRecord.id.asc()).all()
        return [PageRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def add_page(
    sourcetitle: str,
    tr_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    mdwiki_revid: int | None = None,
    word: int = 0,
) -> PageRecord:
    """Add a page and return the created record."""
    if not sourcetitle:
        raise ValueError("Title is required")
    with get_session() as session:
        orm_obj = _PageRecord(
            title=sourcetitle,
            word=word,
            translate_type=tr_type,
            cat=cat,
            lang=lang,
            user=user,
            pupdate=func.current_date(),
            target=target,
            mdwiki_revid=mdwiki_revid,
        )
        session.add(orm_obj)
        try:
            session.commit()
            session.refresh(orm_obj)
            return PageRecord(**orm_obj.to_dict())
        except IntegrityError as e:
            logger.error(f"Failed to add page (integrity error): {e}")
            session.rollback()
            raise ValueError(f"Page with title '{sourcetitle}' already exists") from e
        except Exception as e:
            logger.error(f"Failed to add page: {e}")
            session.rollback()
            raise


def insert_page_target(
    sourcetitle: str,
    tr_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    mdwiki_revid: int | None = None,
    word: int = 0,
) -> bool:
    """Insert a page target record and return success status."""
    try:
        add_page(
            sourcetitle=sourcetitle,
            tr_type=tr_type,
            cat=cat,
            lang=lang,
            user=user,
            target=target,
            mdwiki_revid=mdwiki_revid,
            word=word,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to insert page target: {e}")
        return False


def update_page(
    page_id: int,
    title: str,
    target: str,
    translate_type: str | None = None,
    cat: str | None = None,
    lang: str | None = None,
    user: str | None = None,
    mdwiki_revid: int | None = None,
    word: int | None = None,
    add_date: str | None = None,
    deleted: int | None = None,
) -> PageRecord:
    """Update page."""
    with get_session() as session:
        orm_obj = session.query(_PageRecord).filter(_PageRecord.id == page_id).first()
        if not orm_obj:
            raise LookupError(f"Page id {page_id} was not found")

        orm_obj.title = title
        orm_obj.target = target
        if translate_type is not None:
            orm_obj.translate_type = translate_type
        if cat is not None:
            orm_obj.cat = cat
        if lang is not None:
            orm_obj.lang = lang
        if user is not None:
            orm_obj.user = user
        if mdwiki_revid is not None:
            orm_obj.mdwiki_revid = mdwiki_revid
        if word is not None:
            orm_obj.word = word
        if add_date is not None:
            orm_obj.add_date = add_date
        if deleted is not None:
            orm_obj.deleted = deleted

        session.commit()
        session.refresh(orm_obj)
        return PageRecord(**orm_obj.to_dict())


def delete_page(page_id: int) -> PageRecord:
    """Delete a page."""
    with get_session() as session:
        orm_obj = session.query(_PageRecord).filter(_PageRecord.id == page_id).first()
        if not orm_obj:
            raise LookupError(f"Page id {page_id} was not found")

        record = PageRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def find_exists_or_update_page(
    title: str,
    lang: str,
    user: str,
    target: str,
) -> bool:
    """Check if record exists and update target if empty."""

    with get_session() as session:
        # Check existence
        orm_objs = (
            session.query(_PageRecord)
            .filter(
                _PageRecord.title == title,
                _PageRecord.lang == lang,
                _PageRecord.user == user,
            )
            .all()
        )

        if orm_objs:
            changed = False
            for obj in orm_objs:
                # Update target if it's empty or NULL
                if not obj.target:
                    obj.target = target
                    obj.pupdate = func.current_date()
                    changed = True
            if changed:
                try:
                    session.commit()
                except Exception as e:
                    logger.error(f"Failed to update page target: {e}")
                    session.rollback()

        return len(orm_objs) > 0


def list_of_users_by_translations_count() -> dict[str, int]:
    """
    Get a dictionary of users and their translation counts.

    Returns:
        Dictionary mapping username to count of published translations,
        ordered by count descending.
    """
    result: dict[str, int] = {}
    with get_session() as session:
        # Query: SELECT user, COUNT(target) as count FROM pages WHERE target != '' GROUP BY user ORDER BY count DESC
        rows = (
            session.query(_PageRecord.user, func.count(_PageRecord.target).label("count"))
            .filter(_PageRecord.target != "")
            .filter(_PageRecord.target.isnot(None))
            .group_by(_PageRecord.user)
            .order_by(func.count(_PageRecord.target).desc())
            .all()
        )
        for user, count in rows:
            if user is not None:
                result[user] = count
    return result


__all__ = [
    "list_pages",
    "add_page",
    "update_page",
    "delete_page",
    "find_exists_or_update_page",
    "insert_page_target",
    "list_of_users_by_translations_count",
]
