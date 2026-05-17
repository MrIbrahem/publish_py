"""
SQLAlchemy-based service for managing refs counts.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import RefsCountRecord

logger = logging.getLogger(__name__)


def list_refs_counts() -> List[RefsCountRecord]:
    """Return all refs_count records."""
    orm_objs = db.session.query(RefsCountRecord).order_by(RefsCountRecord.r_id.asc()).all()
    return orm_objs


def get_refs_count(refs_id: int) -> RefsCountRecord | None:
    """Get a refs_count record by ID."""
    orm_obj = db.session.get(RefsCountRecord, refs_id)
    if not orm_obj:
        logger.warning(f"RefsCount record with ID {refs_id} not found")
        return None
    return orm_obj


def get_refs_count_by_title(title: str) -> RefsCountRecord | None:
    """Get a refs_count record by title."""
    orm_obj = db.session.query(RefsCountRecord).filter(RefsCountRecord.r_title == title).first()
    if not orm_obj:
        return None
    return orm_obj


def add_refs_count(
    r_title: str,
    r_lead_refs: int | None = None,
    r_all_refs: int | None = None,
) -> RefsCountRecord:
    """Add a new refs_count record."""
    r_title = r_title.strip()
    if not r_title:
        raise ValueError("Title is required")

    orm_obj = RefsCountRecord(r_title=r_title, r_lead_refs=r_lead_refs, r_all_refs=r_all_refs)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Refs count for '{r_title}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def add_or_update_refs_count(
    r_title: str,
    r_lead_refs: int | None = None,
    r_all_refs: int | None = None,
) -> RefsCountRecord:
    """Add or update a refs_count record."""
    r_title = r_title.strip()
    if not r_title:
        raise ValueError("Title is required")

    orm_obj = db.session.query(RefsCountRecord).filter(RefsCountRecord.r_title == r_title).first()
    if orm_obj:
        orm_obj.r_lead_refs = r_lead_refs
        orm_obj.r_all_refs = r_all_refs
    else:
        orm_obj = RefsCountRecord(r_title=r_title, r_lead_refs=r_lead_refs, r_all_refs=r_all_refs)
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_refs_count(refs_id: int, **kwargs) -> RefsCountRecord:
    """Update a refs_count record."""
    orm_obj = db.session.get(RefsCountRecord, refs_id)
    if not orm_obj:
        raise ValueError(f"RefsCount record with ID {refs_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_refs_count(refs_id: int) -> bool:
    """Delete a refs_count record by ID."""
    # orm_obj = db.session.get(RefsCountRecord, refs_id)
    orm_obj = db.session.get(RefsCountRecord, refs_id)
    if not orm_obj:
        raise ValueError(f"RefsCount record with ID {refs_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(RefsCountRecord, refs_id)
    return deleted is None


def get_ref_counts_for_title(title: str) -> tuple[int | None, int | None]:
    """Get lead and all reference counts for a title."""
    record = get_refs_count_by_title(title)
    if record:
        return record.r_lead_refs, record.r_all_refs
    return None, None


__all__ = [
    "list_refs_counts",
    "get_refs_count",
    "get_refs_count_by_title",
    "add_refs_count",
    "add_or_update_refs_count",
    "update_refs_count",
    "delete_refs_count",
    "get_ref_counts_for_title",
]
