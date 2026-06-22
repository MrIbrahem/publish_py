"""
SQLAlchemy-based service for managing translate types.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import UniqueError, db
from ...models import PageRecord, QidRecord, TranslateTypeRecord

logger = logging.getLogger(__name__)


def list_translate_types(cat: str = "All") -> List[TranslateTypeRecord]:
    """Return translate_type records, optionally filtered by category membership.

    When ``cat != "All"``, only records whose ``tt_title`` matches a page in the
    given category are returned.
    """
    query = db.session.query(TranslateTypeRecord)
    if cat and cat != "All":
        titles_in_cat = db.session.query(PageRecord.title).filter(PageRecord.cat == cat).distinct()
        query = query.filter(TranslateTypeRecord.tt_title.in_(titles_in_cat))
    return query.order_by(TranslateTypeRecord.tt_id.asc()).all()


def list_new_titles() -> List[str]:
    """Return titles in the qids table that are not yet in translate_type."""
    existing_titles = db.session.query(TranslateTypeRecord.tt_title).subquery()
    rows = (
        db.session.query(QidRecord.title)
        .filter(QidRecord.title.notin_(db.session.query(existing_titles.c.tt_title)))
        .distinct()
        .order_by(QidRecord.title.asc())
        .all()
    )
    return [row[0] for row in rows if row[0]]


def list_lead_enabled_types() -> List[TranslateTypeRecord]:
    """Return translate_type records with lead enabled."""
    orm_objs = (
        db.session.query(TranslateTypeRecord)
        .filter(TranslateTypeRecord.tt_lead == 1)
        .order_by(TranslateTypeRecord.tt_id.asc())
        .all()
    )
    return orm_objs


def list_full_enabled_types() -> List[TranslateTypeRecord]:
    """Return translate_type records with full enabled."""
    orm_objs = (
        db.session.query(TranslateTypeRecord)
        .filter(TranslateTypeRecord.tt_full == 1)
        .order_by(TranslateTypeRecord.tt_id.asc())
        .all()
    )
    return orm_objs


def get_translate_type(tt_id: int) -> TranslateTypeRecord | None:
    """Get a translate_type record by ID."""
    # orm_obj = db.session.query(TranslateTypeRecord).filter(TranslateTypeRecord.tt_id == tt_id).first()
    # tt_id is the primary key for TranslateTypeRecord
    orm_obj = db.session.get(TranslateTypeRecord, tt_id)
    if not orm_obj:
        logger.warning(f"TranslateType record with ID {tt_id} not found")
        return None
    return orm_obj


def get_translate_type_by_title(title: str) -> TranslateTypeRecord | None:
    """Get a translate_type record by title."""
    orm_obj = db.session.query(TranslateTypeRecord).filter(TranslateTypeRecord.tt_title == title).first()
    if not orm_obj:
        return None
    return orm_obj


def add_translate_type(
    tt_title: str,
    tt_lead: int = 1,
    tt_full: int = 0,
) -> TranslateTypeRecord:
    """Add a new translate_type record."""
    tt_title = tt_title.strip()
    if not tt_title:
        raise ValueError("Title is required")

    orm_obj = TranslateTypeRecord(tt_title=tt_title, tt_lead=tt_lead, tt_full=tt_full)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise UniqueError(title=tt_title) from None

    db.session.refresh(orm_obj)
    return orm_obj


def update_translate_type(
    tt_id: int,
    tt_title: str | None = None,
    tt_lead: int | None = None,
    tt_full: int | None = None,
) -> TranslateTypeRecord:
    """Update a translate_type record."""
    # tt_id is the primary key for TranslateTypeRecord
    orm_obj = db.session.get(TranslateTypeRecord, tt_id)
    if not orm_obj:
        raise ValueError(f"TranslateType record with ID {tt_id} not found")

    if tt_title:
        tt_title = tt_title.strip()
        orm_obj.tt_title = tt_title

    if tt_lead is not None:
        orm_obj.tt_lead = int(tt_lead)

    if tt_full is not None:
        orm_obj.tt_full = int(tt_full)

    try:
        db.session.commit()
        db.session.refresh(orm_obj)
    except IntegrityError:
        db.session.rollback()
        raise UniqueError(title=tt_title) from None
    except Exception:
        db.session.rollback()
        raise
    return orm_obj


def can_translate_lead(title: str) -> bool:
    """Check if a title can be translated as lead."""
    record = get_translate_type_by_title(title)
    return record.tt_lead == 1 if record else True


def can_translate_full(title: str) -> bool:
    """Check if a title can be translated as full."""
    record = get_translate_type_by_title(title)
    return record.tt_full == 1 if record else False


__all__ = [
    "list_translate_types",
    "list_new_titles",
    "list_lead_enabled_types",
    "list_full_enabled_types",
    "get_translate_type",
    "get_translate_type_by_title",
    "add_translate_type",
    "update_translate_type",
    "can_translate_lead",
    "can_translate_full",
]
