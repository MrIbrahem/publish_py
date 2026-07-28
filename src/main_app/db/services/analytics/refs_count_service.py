"""
SQLAlchemy-based service for managing refs counts.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import RefsCountRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class RefsCountService(CRUDService[RefsCountRecord]):
    model = RefsCountRecord

    def __init__(self):
        super().__init__(db.session, RefsCountRecord)


refs_count_crud = RefsCountService()


def list_refs_counts() -> list[RefsCountRecord]:
    """Return all refs_count records."""
    return list(
        refs_count_crud.list(
            order_by=[RefsCountRecord.r_id.asc()],
        )
    )


def get_refs_count(refs_id: int) -> RefsCountRecord | None:
    """Get a refs_count record by ID."""
    orm_obj = refs_count_crud.get(refs_id)
    if not orm_obj:
        logger.warning(f"RefsCount record with ID {refs_id} not found")
        return None
    return orm_obj


def get_refs_count_by_title(title: str) -> RefsCountRecord | None:
    """Get a refs_count record by title."""
    return refs_count_crud.get_by(r_title=title)


def add_refs_count(
    r_title: str,
    r_lead_refs: int | None = None,
    r_all_refs: int | None = None,
) -> RefsCountRecord:
    """Add a new refs_count record."""
    r_title = r_title.strip()
    if not r_title:
        raise ValueError("Title is required")

    try:
        return refs_count_crud.create(r_title=r_title, r_lead_refs=r_lead_refs, r_all_refs=r_all_refs)
    except IntegrityError:
        raise ValueError(f"Refs count for '{r_title}' already exists") from None


def add_or_update_refs_count(
    r_title: str,
    r_lead_refs: int | None = None,
    r_all_refs: int | None = None,
) -> RefsCountRecord:
    """Add or update a refs_count record."""
    r_title = r_title.strip()
    if not r_title:
        raise ValueError("Title is required")

    instance, is_new = refs_count_crud.upsert_by(
        keys={"r_title": r_title},
        r_lead_refs=r_lead_refs,
        r_all_refs=r_all_refs,
    )
    return instance


def update_refs_count(refs_id: int, **kwargs) -> RefsCountRecord | None:
    """Update a refs_count record."""
    return refs_count_crud.update_or_404(refs_id, **kwargs)


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
    "get_ref_counts_for_title",
]
