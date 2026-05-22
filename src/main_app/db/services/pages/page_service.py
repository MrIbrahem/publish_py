"""
SQLAlchemy-based service for managing pages and page targets.
"""

from __future__ import annotations

import logging
from typing import Any, List

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import PageRecord

logger = logging.getLogger(__name__)


def list_pages() -> List[PageRecord]:
    """Return all pages."""
    orm_objs = db.session.query(PageRecord).order_by(PageRecord.id.asc()).all()
    return orm_objs


def list_pages_by_lang_cat(lang: str, cat: str) -> List[PageRecord]:
    """Return pages filtered by language and category."""
    return db.session.query(PageRecord).filter(PageRecord.lang == lang, PageRecord.cat == cat).all()


def add_page(
    sourcetitle: str,
    translate_type: str,
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
    orm_obj = PageRecord(
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


def insert_page_target(
    sourcetitle: str,
    translate_type: str,
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
    orm_obj = db.session.get(PageRecord, page_id)
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

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_page(page_id: int) -> bool:
    """Delete a page."""
    # orm_obj = db.session.query(PageRecord).filter(PageRecord.id == page_id).first()
    orm_obj = db.session.get(PageRecord, page_id)
    if not orm_obj:
        raise LookupError(f"Page id {page_id} was not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(PageRecord, page_id)
    return deleted is None


def find_exists_or_update_page(
    title: str,
    lang: str,
    user: str,
    target: str,
) -> bool:
    """Check if record exists and update target if empty."""

    # Check existence
    orm_objs = (
        db.session.query(PageRecord)
        .filter(
            PageRecord.title == title,
            PageRecord.lang == lang,
            PageRecord.user == user,
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
                db.session.commit()
            except Exception as e:
                logger.error(f"Failed to update page target: {e}")
                db.session.rollback()
                # raise

    return len(orm_objs) > 0


def list_of_users_by_translations_count() -> dict[str, int]:
    """
    Get a dictionary of users and their translation counts.

    Returns:
        Dictionary mapping username to count of published translations,
        ordered by count descending.
    """
    result: dict[str, int] = {}
    # Query: SELECT user, COUNT(target) as count FROM pages WHERE target != '' GROUP BY user ORDER BY count DESC
    rows = (
        db.session.query(PageRecord.user, func.count(PageRecord.target).label("count"))
        .filter(PageRecord.target != "")
        .filter(PageRecord.target.isnot(None))
        .group_by(PageRecord.user)
        .order_by(db.func.count(PageRecord.target).desc())
        .all()
    )
    for user, count in rows:
        if user is not None:
            result[user] = count
    return result


__all__ = [
    "list_pages",
    "list_pages_by_lang_cat",
    "add_page",
    "update_page",
    "delete_page",
    "find_exists_or_update_page",
    "insert_page_target",
    "list_of_users_by_translations_count",
]
