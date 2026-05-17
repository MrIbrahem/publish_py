"""
SQLAlchemy-based service for managing views new.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import ViewsNewRecord

logger = logging.getLogger(__name__)


def list_views_new() -> List[ViewsNewRecord]:
    """Return all views_new records."""
    orm_objs = db.session.query(ViewsNewRecord).order_by(ViewsNewRecord.id.asc()).all()
    return orm_objs


def list_views_by_target(target: str) -> List[ViewsNewRecord]:
    """Return views_new records for a specific target."""
    orm_objs = (
        db.session.query(ViewsNewRecord)
        .filter(ViewsNewRecord.target == target)
        .order_by(ViewsNewRecord.year.desc())
        .all()
    )
    return orm_objs


def list_views_by_lang(lang: str) -> List[ViewsNewRecord]:
    """Return views_new records for a specific language."""
    orm_objs = (
        db.session.query(ViewsNewRecord).filter(ViewsNewRecord.lang == lang).order_by(ViewsNewRecord.id.asc()).all()
    )
    return orm_objs


def get_views_new(view_id: int) -> ViewsNewRecord | None:
    """Get a views_new record by ID."""
    orm_obj = db.session.query(ViewsNewRecord).filter(ViewsNewRecord.id == view_id).first()
    if not orm_obj:
        logger.warning(f"ViewsNew record with ID {view_id} not found")
        return None
    return orm_obj


def get_views_by_target_lang_year(target: str, lang: str, year: int) -> ViewsNewRecord | None:
    """Get a views_new record by target, language, and year."""
    orm_obj = (
        db.session.query(ViewsNewRecord)
        .filter(ViewsNewRecord.target == target)
        .filter(ViewsNewRecord.lang == lang)
        .filter(ViewsNewRecord.year == year)
        .first()
    )
    if not orm_obj:
        return None
    return orm_obj


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

    orm_obj = ViewsNewRecord(target=target, lang=lang, year=year, views=views)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Views record for '{target}' in '{lang}' for year {year} already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


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

    orm_obj = (
        db.session.query(ViewsNewRecord)
        .filter(ViewsNewRecord.target == target)
        .filter(ViewsNewRecord.lang == lang)
        .filter(ViewsNewRecord.year == year)
        .first()
    )
    if orm_obj:
        orm_obj.views = views
    else:
        orm_obj = ViewsNewRecord(target=target, lang=lang, year=year, views=views)
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_views_new(view_id: int, **kwargs) -> ViewsNewRecord:
    """Update a views_new record."""
    orm_obj = db.session.query(ViewsNewRecord).filter(ViewsNewRecord.id == view_id).first()
    if not orm_obj:
        raise ValueError(f"ViewsNew record with ID {view_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_views_new(view_id: int) -> ViewsNewRecord:
    """Delete a views_new record by ID."""
    orm_obj = db.session.query(ViewsNewRecord).filter(ViewsNewRecord.id == view_id).first()
    if not orm_obj:
        raise ValueError(f"ViewsNew record with ID {view_id} not found")

    record = ViewsNewRecord(**orm_obj.to_dict())
    db.session.delete(orm_obj)
    db.session.commit()
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
