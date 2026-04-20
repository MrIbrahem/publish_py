"""
SQLAlchemy-based service for managing pages and page targets.
"""

from __future__ import annotations

import logging
from typing import Any, List

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from ...db_models.shared_models import PageRecord
from ..engine import get_session
from ..models import _PageRecord

logger = logging.getLogger(__name__)


def list_pages() -> List[PageRecord]:
    """Return all pages."""
    with get_session() as session:
        orm_objs = session.query(_PageRecord).order_by(_PageRecord.id.asc()).all()
        return [PageRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def add_page(title: str, main_file: str) -> PageRecord:
    """Add a page."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = _PageRecord(title=title, target=main_file)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Page '{title}' already exists") from None

        session.refresh(orm_obj)
        return PageRecord(**orm_obj.to_dict())


def add_or_update_page(title: str, main_file: str) -> PageRecord:
    """Add or update a page."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = session.query(_PageRecord).filter(_PageRecord.title == title).first()
        if orm_obj:
            orm_obj.target = main_file
        else:
            orm_obj = _PageRecord(title=title, target=main_file)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return PageRecord(**orm_obj.to_dict())


def update_page(page_id: int, title: str, main_file: str) -> PageRecord:
    """Update page."""
    with get_session() as session:
        orm_obj = session.query(_PageRecord).filter(_PageRecord.id == page_id).first()
        if not orm_obj:
            raise LookupError(f"Page id {page_id} was not found")

        orm_obj.title = title
        orm_obj.target = main_file

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
    """Insert a page target record."""
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
            return True
        except Exception as e:
            logger.error(f"Failed to insert page target: {e}")
            session.rollback()
            return False


__all__ = [
    "list_pages",
    "add_page",
    "add_or_update_page",
    "update_page",
    "delete_page",
    "find_exists_or_update_page",
    "insert_page_target",
]
