"""Utilities for managing coordinators."""

from __future__ import annotations

import functools
import logging
from typing import List

from ....config import settings
from ....shared.domain.services.db_service import has_db_config
from ..db.db_coordinators import CoordinatorsDB
from ..models.coordinator import CoordinatorRecord

logger = logging.getLogger(__name__)

_COORDINATORS_STORE: CoordinatorsDB | None = None


def get_coordinators_db() -> CoordinatorsDB:
    global _COORDINATORS_STORE

    if _COORDINATORS_STORE is None:
        if not has_db_config():
            raise RuntimeError("CoordinatorsDB requires database configuration; no fallback store is available.")

        try:
            _COORDINATORS_STORE = CoordinatorsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL CoordinatorsDB")
            raise RuntimeError("Unable to initialize CoordinatorsDB") from exc

    return _COORDINATORS_STORE


def list_coordinators() -> List[CoordinatorRecord]:
    """Return all coordinator records."""
    store = get_coordinators_db()
    return store.list()


@functools.lru_cache(maxsize=1)
def active_coordinators() -> List[CoordinatorRecord]:
    """Return all active coordinator records."""
    store = get_coordinators_db()
    return [u.username for u in store.list() if u.is_active]


def get_coordinator(coordinator_id: int) -> CoordinatorRecord | None:
    """Get a coordinator record by ID."""
    store = get_coordinators_db()
    return store.fetch_by_id(coordinator_id)


def get_coordinator_by_user(username: str) -> CoordinatorRecord | None:
    """Get a coordinator record by username."""
    store = get_coordinators_db()
    return store.fetch_by_user(username)


def add_coordinator(username: str, is_active: int = 1) -> CoordinatorRecord:
    """Add a new coordinator record."""
    store = get_coordinators_db()
    record = store.add(username, is_active)
    active_coordinators.cache_clear()  # Clear the cache to ensure active coordinators list is updated
    return record


def add_or_update_coordinator(username: str, is_active: int = 1) -> CoordinatorRecord:
    """Add or update a coordinator record."""
    store = get_coordinators_db()
    record = store.add_or_update(username, is_active)
    active_coordinators.cache_clear()  # Clear the cache to ensure active coordinators list is updated
    return record


def update_coordinator(coordinator_id: int, **kwargs) -> CoordinatorRecord:
    """Update a coordinator record."""
    store = get_coordinators_db()
    record = store.update(coordinator_id, **kwargs)
    active_coordinators.cache_clear()  # Clear the cache to ensure active coordinators list is updated
    return record


def delete_coordinator(coordinator_id: int) -> CoordinatorRecord:
    """Delete a coordinator record by ID."""
    store = get_coordinators_db()
    record = store.delete(coordinator_id)
    active_coordinators.cache_clear()  # Clear the cache to ensure active coordinators list is updated
    return record


def is_coordinator(username: str) -> bool:
    """Check if a username is a coordinator."""
    store = get_coordinators_db()
    record = store.fetch_by_user(username)
    return record is not None and record.is_active == 1


def set_coordinator_active(coordinator_id: int, is_active: bool) -> CoordinatorRecord:
    """Toggle coordinator activity and refresh settings."""

    store = get_coordinators_db()
    record = store.set_active(coordinator_id, is_active)
    active_coordinators.cache_clear()  # Clear the cache to ensure active coordinators list is updated
    return record


__all__ = [
    "get_coordinators_db",
    "list_coordinators",
    "active_coordinators",
    "get_coordinator",
    "get_coordinator_by_user",
    "add_coordinator",
    "add_or_update_coordinator",
    "update_coordinator",
    "delete_coordinator",
    "is_coordinator",
    "set_coordinator_active",
]
