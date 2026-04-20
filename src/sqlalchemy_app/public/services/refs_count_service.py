"""
SQLAlchemy-based service for managing refs counts.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....db_models.public_models import RefsCountRecord
from ...shared.engine import get_session
from ..models import _RefsCountRecord

logger = logging.getLogger(__name__)


def list_refs_counts() -> List[RefsCountRecord]:
    """Return all refs_count records."""
    with get_session() as session:
        orm_objs = session.query(_RefsCountRecord).order_by(_RefsCountRecord.r_id.asc()).all()
        return [RefsCountRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_refs_count(refs_id: int) -> RefsCountRecord | None:
    """Get a refs_count record by ID."""
    with get_session() as session:
        orm_obj = session.query(_RefsCountRecord).filter(_RefsCountRecord.r_id == refs_id).first()
        if not orm_obj:
            logger.warning(f"RefsCount record with ID {refs_id} not found")
            return None
        return RefsCountRecord(**orm_obj.to_dict())


def get_refs_count_by_title(title: str) -> RefsCountRecord | None:
    """Get a refs_count record by title."""
    with get_session() as session:
        orm_obj = session.query(_RefsCountRecord).filter(_RefsCountRecord.r_title == title).first()
        if not orm_obj:
            return None
        return RefsCountRecord(**orm_obj.to_dict())


def add_refs_count(
    r_title: str,
    r_lead_refs: int | None = None,
    r_all_refs: int | None = None,
) -> RefsCountRecord:
    """Add a new refs_count record."""
    r_title = r_title.strip()
    if not r_title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = _RefsCountRecord(r_title=r_title, r_lead_refs=r_lead_refs, r_all_refs=r_all_refs)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Refs count for '{r_title}' already exists") from None

        session.refresh(orm_obj)
        return RefsCountRecord(**orm_obj.to_dict())


def add_or_update_refs_count(
    r_title: str,
    r_lead_refs: int | None = None,
    r_all_refs: int | None = None,
) -> RefsCountRecord:
    """Add or update a refs_count record."""
    r_title = r_title.strip()
    if not r_title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = session.query(_RefsCountRecord).filter(_RefsCountRecord.r_title == r_title).first()
        if orm_obj:
            orm_obj.r_lead_refs = r_lead_refs
            orm_obj.r_all_refs = r_all_refs
        else:
            orm_obj = _RefsCountRecord(r_title=r_title, r_lead_refs=r_lead_refs, r_all_refs=r_all_refs)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return RefsCountRecord(**orm_obj.to_dict())


def update_refs_count(refs_id: int, **kwargs) -> RefsCountRecord:
    """Update a refs_count record."""
    with get_session() as session:
        orm_obj = session.query(_RefsCountRecord).filter(_RefsCountRecord.r_id == refs_id).first()
        if not orm_obj:
            raise ValueError(f"RefsCount record with ID {refs_id} not found")

        if not kwargs:
            return RefsCountRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return RefsCountRecord(**orm_obj.to_dict())


def delete_refs_count(refs_id: int) -> RefsCountRecord:
    """Delete a refs_count record by ID."""
    with get_session() as session:
        orm_obj = session.query(_RefsCountRecord).filter(_RefsCountRecord.r_id == refs_id).first()
        if not orm_obj:
            raise ValueError(f"RefsCount record with ID {refs_id} not found")

        record = RefsCountRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


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
