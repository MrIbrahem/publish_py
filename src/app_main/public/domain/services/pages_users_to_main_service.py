"""Utilities for managing pages_users_to_main."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ....shared.domain.db_service import has_db_config
from ..db.db_pages_users_to_main import PagesUsersToMainDB
from ..models.pages_users_to_main import PagesUsersToMainRecord

logger = logging.getLogger(__name__)

_PAGES_USERS_TO_MAIN_STORE: PagesUsersToMainDB | None = None


def get_pages_users_to_main_db() -> PagesUsersToMainDB:
    global _PAGES_USERS_TO_MAIN_STORE

    if _PAGES_USERS_TO_MAIN_STORE is None:
        if not has_db_config():
            raise RuntimeError("PagesUsersToMainDB requires database configuration; no fallback store is available.")

        try:
            _PAGES_USERS_TO_MAIN_STORE = PagesUsersToMainDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL PagesUsersToMainDB")
            raise RuntimeError("Unable to initialize PagesUsersToMainDB") from exc

    return _PAGES_USERS_TO_MAIN_STORE


def list_pages_users_to_main() -> List[PagesUsersToMainRecord]:
    """Return all pages_users_to_main records."""
    store = get_pages_users_to_main_db()
    return store.list()


def get_pages_users_to_main(record_id: int) -> PagesUsersToMainRecord | None:
    """Get a pages_users_to_main record by ID."""
    store = get_pages_users_to_main_db()
    return store.fetch_by_id(record_id)


def add_pages_users_to_main(
    new_target: str = "",
    new_user: str = "",
    new_qid: str = "",
) -> PagesUsersToMainRecord:
    """Add a new pages_users_to_main record."""
    store = get_pages_users_to_main_db()
    return store.add(new_target, new_user, new_qid)


def update_pages_users_to_main(record_id: int, **kwargs) -> PagesUsersToMainRecord:
    """Update a pages_users_to_main record."""
    store = get_pages_users_to_main_db()
    return store.update(record_id, **kwargs)


def delete_pages_users_to_main(record_id: int) -> PagesUsersToMainRecord:
    """Delete a pages_users_to_main record by ID."""
    store = get_pages_users_to_main_db()
    return store.delete(record_id)


__all__ = [
    "get_pages_users_to_main_db",
    "list_pages_users_to_main",
    "get_pages_users_to_main",
    "add_pages_users_to_main",
    "update_pages_users_to_main",
    "delete_pages_users_to_main",
]
