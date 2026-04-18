"""Utilities for managing users."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ....shared.domain.db_service import has_db_config
from ..db.db_users import UsersDB
from ..models.user import UserRecord

logger = logging.getLogger(__name__)

_USERS_STORE: UsersDB | None = None


def get_users_db() -> UsersDB:
    global _USERS_STORE

    if _USERS_STORE is None:
        if not has_db_config():
            raise RuntimeError("UsersDB requires database configuration; no fallback store is available.")

        try:
            _USERS_STORE = UsersDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL UsersDB")
            raise RuntimeError("Unable to initialize UsersDB") from exc

    return _USERS_STORE


def list_users() -> List[UserRecord]:
    """Return all user records."""
    store = get_users_db()
    return store.list()


def list_users_by_group(user_group: str) -> List[UserRecord]:
    """Return user records by group."""
    store = get_users_db()
    return store.list_by_group(user_group)


def get_user(user_id: int) -> UserRecord | None:
    """Get a user record by ID."""
    store = get_users_db()
    return store.fetch_by_id(user_id)


def get_user_by_username(username: str) -> UserRecord | None:
    """Get a user record by username."""
    store = get_users_db()
    return store.fetch_by_username(username)


def add_user(
    username: str,
    email: str = "",
    wiki: str = "",
    user_group: str = "Uncategorized",
) -> UserRecord:
    """Add a new user record."""
    store = get_users_db()
    return store.add(username, email, wiki, user_group)


def add_or_update_user(
    username: str,
    email: str = "",
    wiki: str = "",
    user_group: str = "Uncategorized",
) -> UserRecord:
    """Add or update a user record."""
    store = get_users_db()
    return store.add_or_update(username, email, wiki, user_group)


def update_user(user_id: int, **kwargs) -> UserRecord:
    """Update a user record."""
    store = get_users_db()
    return store.update(user_id, **kwargs)


def delete_user(user_id: int) -> UserRecord:
    """Delete a user record by ID."""
    store = get_users_db()
    return store.delete(user_id)


def user_exists(username: str) -> bool:
    """Check if a user exists."""
    store = get_users_db()
    record = store.fetch_by_username(username)
    return record is not None


__all__ = [
    "get_users_db",
    "list_users",
    "list_users_by_group",
    "get_user",
    "get_user_by_username",
    "add_user",
    "add_or_update_user",
    "update_user",
    "delete_user",
    "user_exists",
]
