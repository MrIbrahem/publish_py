"""Utilities for managing refs_counts."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ....shared.domain.db_service import has_db_config
from ..db.db_refs_counts import RefsCountsDB
from ..models import RefsCountRecord

logger = logging.getLogger(__name__)

_REFS_COUNTS_STORE: RefsCountsDB | None = None


def get_refs_counts_db() -> RefsCountsDB:
    global _REFS_COUNTS_STORE

    if _REFS_COUNTS_STORE is None:
        if not has_db_config():
            raise RuntimeError("RefsCountsDB requires database configuration; no fallback store is available.")

        try:
            _REFS_COUNTS_STORE = RefsCountsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL RefsCountsDB")
            raise RuntimeError("Unable to initialize RefsCountsDB") from exc

    return _REFS_COUNTS_STORE


def list_refs_counts() -> List[RefsCountRecord]:
    """Return all refs_count records."""
    store = get_refs_counts_db()
    return store.list()


def get_refs_count(refs_id: int) -> RefsCountRecord | None:
    """Get a refs_count record by ID."""
    store = get_refs_counts_db()
    return store.fetch_by_id(refs_id)


def get_refs_count_by_title(title: str) -> RefsCountRecord | None:
    """Get a refs_count record by title."""
    store = get_refs_counts_db()
    return store.fetch_by_title(title)


def add_refs_count(
    r_title: str,
    r_lead_refs: int | None = None,
    r_all_refs: int | None = None,
) -> RefsCountRecord:
    """Add a new refs_count record."""
    store = get_refs_counts_db()
    return store.add(r_title, r_lead_refs, r_all_refs)


def add_or_update_refs_count(
    r_title: str,
    r_lead_refs: int | None = None,
    r_all_refs: int | None = None,
) -> RefsCountRecord:
    """Add or update a refs_count record."""
    store = get_refs_counts_db()
    return store.add_or_update(r_title, r_lead_refs, r_all_refs)


def update_refs_count(refs_id: int, **kwargs) -> RefsCountRecord:
    """Update a refs_count record."""
    store = get_refs_counts_db()
    return store.update(refs_id, **kwargs)


def delete_refs_count(refs_id: int) -> RefsCountRecord:
    """Delete a refs_count record by ID."""
    store = get_refs_counts_db()
    return store.delete(refs_id)


def get_ref_counts_for_title(title: str) -> tuple[int | None, int | None]:
    """Get lead and all reference counts for a title."""
    store = get_refs_counts_db()
    record = store.fetch_by_title(title)
    if record:
        return record.r_lead_refs, record.r_all_refs
    return None, None


__all__ = [
    "get_refs_counts_db",
    "list_refs_counts",
    "get_refs_count",
    "get_refs_count_by_title",
    "add_refs_count",
    "add_or_update_refs_count",
    "update_refs_count",
    "delete_refs_count",
    "get_ref_counts_for_title",
]
