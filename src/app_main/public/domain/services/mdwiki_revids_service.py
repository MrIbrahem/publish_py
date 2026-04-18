"""Utilities for managing mdwiki_revids."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings

from ..db.db_mdwiki_revids import MdwikiRevidsDB
from ..models import MdwikiRevidRecord

logger = logging.getLogger(__name__)

_MDWIKI_REVIDS_STORE: MdwikiRevidsDB | None = None


from ....config import has_db_config


def get_mdwiki_revids_db() -> MdwikiRevidsDB:
    global _MDWIKI_REVIDS_STORE

    if _MDWIKI_REVIDS_STORE is None:
        if not has_db_config():
            raise RuntimeError("MdwikiRevidsDB requires database configuration; no fallback store is available.")

        try:
            _MDWIKI_REVIDS_STORE = MdwikiRevidsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL MdwikiRevidsDB")
            raise RuntimeError("Unable to initialize MdwikiRevidsDB") from exc

    return _MDWIKI_REVIDS_STORE


def list_mdwiki_revids() -> List[MdwikiRevidRecord]:
    """Return all mdwiki_revid records."""
    store = get_mdwiki_revids_db()
    return store.list()


def get_mdwiki_revid_by_title(title: str) -> MdwikiRevidRecord | None:
    """Get an mdwiki_revid record by title."""
    store = get_mdwiki_revids_db()
    return store.fetch_by_title(title)


def add_mdwiki_revid(title: str, revid: int) -> MdwikiRevidRecord:
    """Add a new mdwiki_revid record."""
    store = get_mdwiki_revids_db()
    return store.add(title, revid)


def add_or_update_mdwiki_revid(title: str, revid: int) -> MdwikiRevidRecord:
    """Add or update an mdwiki_revid record."""
    store = get_mdwiki_revids_db()
    return store.add_or_update(title, revid)


def update_mdwiki_revid(title: str, revid: int) -> MdwikiRevidRecord:
    """Update an mdwiki_revid record."""
    store = get_mdwiki_revids_db()
    return store.update(title, revid)


def delete_mdwiki_revid(title: str) -> MdwikiRevidRecord:
    """Delete an mdwiki_revid record by title."""
    store = get_mdwiki_revids_db()
    return store.delete(title)


def get_revid_for_title(title: str) -> int | None:
    """Get the revision ID for a title."""
    store = get_mdwiki_revids_db()
    record = store.fetch_by_title(title)
    return record.revid if record else None


__all__ = [
    "get_mdwiki_revids_db",
    "list_mdwiki_revids",
    "get_mdwiki_revid_by_title",
    "add_mdwiki_revid",
    "add_or_update_mdwiki_revid",
    "update_mdwiki_revid",
    "delete_mdwiki_revid",
    "get_revid_for_title",
]
