"""
SQLAlchemy-based service for managing enwiki pageviews.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ..engine import get_session
from ...sqlalchemy_models import EnwikiPageviewRecord

logger = logging.getLogger(__name__)


def list_enwiki_pageviews() -> List[EnwikiPageviewRecord]:
    """Return all enwiki pageview records."""
    with get_session() as session:
        orm_objs = session.query(EnwikiPageviewRecord).order_by(EnwikiPageviewRecord.id.asc()).all()
        return orm_objs


def get_top_enwiki_pageviews(limit: int = 100) -> List[EnwikiPageviewRecord]:
    """Return top enwiki pageview records by view count."""
    with get_session() as session:
        orm_objs = session.query(EnwikiPageviewRecord).order_by(EnwikiPageviewRecord.en_views.desc()).limit(limit).all()
        return orm_objs


def get_enwiki_pageview(pageview_id: int) -> EnwikiPageviewRecord | None:
    """Get an enwiki pageview record by ID."""
    with get_session() as session:
        orm_obj = session.query(EnwikiPageviewRecord).filter(EnwikiPageviewRecord.id == pageview_id).first()
        if not orm_obj:
            logger.warning(f"Enwiki pageview record with ID {pageview_id} not found")
            return None
        return orm_obj


def get_enwiki_pageview_by_title(title: str) -> EnwikiPageviewRecord | None:
    """Get an enwiki pageview record by title."""
    with get_session() as session:
        orm_obj = session.query(EnwikiPageviewRecord).filter(EnwikiPageviewRecord.title == title).first()
        if not orm_obj:
            return None
        return orm_obj


def add_enwiki_pageview(title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
    """Add a new enwiki pageview record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = EnwikiPageviewRecord(title=title, en_views=en_views)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Enwiki pageview for '{title}' already exists") from None

        session.refresh(orm_obj)
        return orm_obj


def add_or_update_enwiki_pageview(title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
    """Add or update an enwiki pageview record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = session.query(EnwikiPageviewRecord).filter(EnwikiPageviewRecord.title == title).first()
        if orm_obj:
            orm_obj.en_views = en_views
        else:
            orm_obj = EnwikiPageviewRecord(title=title, en_views=en_views)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return orm_obj


def update_enwiki_pageview(pageview_id: int, **kwargs) -> EnwikiPageviewRecord:
    """Update an enwiki pageview record."""
    with get_session() as session:
        orm_obj = session.query(EnwikiPageviewRecord).filter(EnwikiPageviewRecord.id == pageview_id).first()
        if not orm_obj:
            raise ValueError(f"Enwiki pageview record with ID {pageview_id} not found")

        if not kwargs:
            return orm_obj

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return orm_obj


def delete_enwiki_pageview(pageview_id: int) -> EnwikiPageviewRecord:
    """Delete an enwiki pageview record by ID."""
    with get_session() as session:
        orm_obj = session.query(EnwikiPageviewRecord).filter(EnwikiPageviewRecord.id == pageview_id).first()
        if not orm_obj:
            raise ValueError(f"Enwiki pageview record with ID {pageview_id} not found")

        record = EnwikiPageviewRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


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
