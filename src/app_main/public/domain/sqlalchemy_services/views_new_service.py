"""
SQLAlchemy-based service for managing views new.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.sqlalchemy_db.engine import get_session
from ..models.views_new import ViewsNewRecord, _ViewsNewRecord

logger = logging.getLogger(__name__)


def list_views_new() -> List[ViewsNewRecord]:
    """Return all views_new records."""
    with get_session() as session:
        orm_objs = session.query(_ViewsNewRecord).order_by(_ViewsNewRecord.id.asc()).all()
        return [ViewsNewRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def list_views_by_target(target: str) -> List[ViewsNewRecord]:
    """Return views_new records for a specific target."""
    with get_session() as session:
        orm_objs = (
            session.query(_ViewsNewRecord)
            .filter(_ViewsNewRecord.target == target)
            .order_by(_ViewsNewRecord.year.desc())
            .all()
        )
        return [ViewsNewRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def list_views_by_lang(lang: str) -> List[ViewsNewRecord]:
    """Return views_new records for a specific language."""
    with get_session() as session:
        orm_objs = (
            session.query(_ViewsNewRecord)
            .filter(_ViewsNewRecord.lang == lang)
            .order_by(_ViewsNewRecord.id.asc())
            .all()
        )
        return [ViewsNewRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_views_new(view_id: int) -> ViewsNewRecord | None:
    """Get a views_new record by ID."""
    with get_session() as session:
        orm_obj = session.query(_ViewsNewRecord).filter(_ViewsNewRecord.id == view_id).first()
        if not orm_obj:
            logger.warning(f"ViewsNew record with ID {view_id} not found")
            return None
        return ViewsNewRecord(**orm_obj.to_dict())


def get_views_by_target_lang_year(target: str, lang: str, year: int) -> ViewsNewRecord | None:
    """Get a views_new record by target, language, and year."""
    with get_session() as session:
        orm_obj = (
            session.query(_ViewsNewRecord)
            .filter(_ViewsNewRecord.target == target)
            .filter(_ViewsNewRecord.lang == lang)
            .filter(_ViewsNewRecord.year == year)
            .first()
        )
        if not orm_obj:
            return None
        return ViewsNewRecord(**orm_obj.to_dict())


def add_views_new(
    target: str,
    lang: str,
    year: int,
    views: int | None = 0,
) -> ViewsNewRecord:
    """Add a new views_new record."""
    target = target.strip()
    lang = lang.strip()

    if not target:
        raise ValueError("Target is required")
    if not lang:
        raise ValueError("Language is required")

    with get_session() as session:
        orm_obj = _ViewsNewRecord(target=target, lang=lang, year=year, views=views)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Views record for '{target}' in '{lang}' for year {year} already exists") from None

        session.refresh(orm_obj)
        return ViewsNewRecord(**orm_obj.to_dict())


def add_or_update_views_new(
    target: str,
    lang: str,
    year: int,
    views: int | None = 0,
) -> ViewsNewRecord:
    """Add or update a views_new record."""
    target = target.strip()
    lang = lang.strip()

    if not target:
        raise ValueError("Target is required")
    if not lang:
        raise ValueError("Language is required")

    with get_session() as session:
        orm_obj = (
            session.query(_ViewsNewRecord)
            .filter(_ViewsNewRecord.target == target)
            .filter(_ViewsNewRecord.lang == lang)
            .filter(_ViewsNewRecord.year == year)
            .first()
        )
        if orm_obj:
            orm_obj.views = views
        else:
            orm_obj = _ViewsNewRecord(target=target, lang=lang, year=year, views=views)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return ViewsNewRecord(**orm_obj.to_dict())


def update_views_new(view_id: int, **kwargs) -> ViewsNewRecord:
    """Update a views_new record."""
    with get_session() as session:
        orm_obj = session.query(_ViewsNewRecord).filter(_ViewsNewRecord.id == view_id).first()
        if not orm_obj:
            raise ValueError(f"ViewsNew record with ID {view_id} not found")

        if not kwargs:
            return ViewsNewRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return ViewsNewRecord(**orm_obj.to_dict())


def delete_views_new(view_id: int) -> ViewsNewRecord:
    """Delete a views_new record by ID."""
    with get_session() as session:
        orm_obj = session.query(_ViewsNewRecord).filter(_ViewsNewRecord.id == view_id).first()
        if not orm_obj:
            raise ValueError(f"ViewsNew record with ID {view_id} not found")

        record = ViewsNewRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def get_total_views_for_target(target: str) -> int:
    """Get total views across all years for a target."""
    records = list_views_by_target(target)
    return sum(r.views or 0 for r in records)


__all__ = [
    "list_views_new",
    "list_views_by_target",
    "list_views_by_lang",
    "get_views_new",
    "get_views_by_target_lang_year",
    "add_views_new",
    "add_or_update_views_new",
    "update_views_new",
    "delete_views_new",
    "get_total_views_for_target",
]
