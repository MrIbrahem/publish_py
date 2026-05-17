"""
SQLAlchemy-based service for managing enwiki pageviews.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import EnwikiPageviewRecord

logger = logging.getLogger(__name__)


def list_enwiki_pageviews() -> List[EnwikiPageviewRecord]:
    """Return all enwiki pageview records."""
    orm_objs = db.session.query(EnwikiPageviewRecord).order_by(EnwikiPageviewRecord.id.asc()).all()
    return orm_objs


def get_top_enwiki_pageviews(limit: int = 100) -> List[EnwikiPageviewRecord]:
    """Return top enwiki pageview records by view count."""
    orm_objs = db.session.query(EnwikiPageviewRecord).order_by(EnwikiPageviewRecord.en_views.desc()).limit(limit).all()
    return orm_objs


def get_enwiki_pageview(pageview_id: int) -> EnwikiPageviewRecord | None:
    """Get an enwiki pageview record by ID."""
    orm_obj = db.session.get(EnwikiPageviewRecord, pageview_id)
    if not orm_obj:
        logger.warning(f"Enwiki pageview record with ID {pageview_id} not found")
        return None
    return orm_obj


def get_enwiki_pageview_by_title(title: str) -> EnwikiPageviewRecord | None:
    """Get an enwiki pageview record by title."""
    orm_obj = db.session.query(EnwikiPageviewRecord).filter(EnwikiPageviewRecord.title == title).first()
    if not orm_obj:
        return None
    return orm_obj


def add_enwiki_pageview(title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
    """Add a new enwiki pageview record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    orm_obj = EnwikiPageviewRecord(title=title, en_views=en_views)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Enwiki pageview for '{title}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def add_or_update_enwiki_pageview(title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
    """Add or update an enwiki pageview record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    orm_obj = db.session.query(EnwikiPageviewRecord).filter(EnwikiPageviewRecord.title == title).first()
    if orm_obj:
        orm_obj.en_views = en_views
    else:
        orm_obj = EnwikiPageviewRecord(title=title, en_views=en_views)
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_enwiki_pageview(pageview_id: int, **kwargs) -> EnwikiPageviewRecord:
    """Update an enwiki pageview record."""
    orm_obj = db.session.get(EnwikiPageviewRecord, pageview_id)
    if not orm_obj:
        raise ValueError(f"Enwiki pageview record with ID {pageview_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_enwiki_pageview(pageview_id: int) -> bool:
    """Delete an enwiki pageview record by ID."""
    orm_obj = db.session.get(EnwikiPageviewRecord, pageview_id)
    if not orm_obj:
        raise ValueError(f"Enwiki pageview record with ID {pageview_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(EnwikiPageviewRecord, pageview_id)
    return deleted is None


__all__ = [
    "list_enwiki_pageviews",
    "get_top_enwiki_pageviews",
    "get_enwiki_pageview",
    "get_enwiki_pageview_by_title",
    "add_enwiki_pageview",
    "add_or_update_enwiki_pageview",
    "update_enwiki_pageview",
    "delete_enwiki_pageview",
]
