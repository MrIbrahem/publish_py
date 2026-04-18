"""Utilities for managing users_no_inprocess."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ..db.db_users_no_inprocess import UsersNoInprocessDB
from ..models import UsersNoInprocessRecord

logger = logging.getLogger(__name__)

_USERS_NO_INPROCESS_STORE: UsersNoInprocessDB | None = None


from ....config import has_db_config


def get_users_no_inprocess_db() -> UsersNoInprocessDB:
    global _USERS_NO_INPROCESS_STORE

    if _USERS_NO_INPROCESS_STORE is None:
        if not has_db_config():
            raise RuntimeError("UsersNoInprocessDB requires database configuration; no fallback store is available.")

        try:
            _USERS_NO_INPROCESS_STORE = UsersNoInprocessDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL UsersNoInprocessDB")
            raise RuntimeError("Unable to initialize UsersNoInprocessDB") from exc

    return _USERS_NO_INPROCESS_STORE


def list_users_no_inprocess() -> List[UsersNoInprocessRecord]:
    """Return all users_no_inprocess records."""
    store = get_users_no_inprocess_db()
    return store.list()


def list_active_users_no_inprocess() -> List[UsersNoInprocessRecord]:
    """Return all active users_no_inprocess records."""
    store = get_users_no_inprocess_db()
    return store.list_active()


def get_users_no_inprocess(record_id: int) -> UsersNoInprocessRecord | None:
    """Get a users_no_inprocess record by ID."""
    store = get_users_no_inprocess_db()
    return store.fetch_by_id(record_id)


def get_users_no_inprocess_by_user(user: str) -> UsersNoInprocessRecord | None:
    """Get a users_no_inprocess record by username."""
    store = get_users_no_inprocess_db()
    return store.fetch_by_user(user)


def add_users_no_inprocess(user: str, active: int = 1) -> UsersNoInprocessRecord:
    """Add a new users_no_inprocess record."""
    store = get_users_no_inprocess_db()
    return store.add(user, active)


def add_or_update_users_no_inprocess(user: str, active: int = 1) -> UsersNoInprocessRecord:
    """Add or update a users_no_inprocess record."""
    store = get_users_no_inprocess_db()
    return store.add_or_update(user, active)


def update_users_no_inprocess(record_id: int, **kwargs) -> UsersNoInprocessRecord:
    """Update a users_no_inprocess record."""
    store = get_users_no_inprocess_db()
    return store.update(record_id, **kwargs)


def delete_users_no_inprocess(record_id: int) -> UsersNoInprocessRecord:
    """Delete a users_no_inprocess record by ID."""
    store = get_users_no_inprocess_db()
    return store.delete(record_id)


def should_hide_from_inprocess(user: str) -> bool:
    """Check if a user should be hidden from in-process list."""
    store = get_users_no_inprocess_db()
    record = store.fetch_by_user(user)
    return record is not None and record.active == 1


__all__ = [
    "get_users_no_inprocess_db",
    "list_users_no_inprocess",
    "list_active_users_no_inprocess",
    "get_users_no_inprocess",
    "get_users_no_inprocess_by_user",
    "add_users_no_inprocess",
    "add_or_update_users_no_inprocess",
    "update_users_no_inprocess",
    "delete_users_no_inprocess",
    "should_hide_from_inprocess",
]
