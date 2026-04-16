"""Utilities for managing coordinators."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ...shared.domain.services.db_service import has_db_config
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


def list_active_coordinators() -> List[CoordinatorRecord]:
    """Return all active coordinator records."""
    store = get_coordinators_db()
    return store.list_active()


def get_coordinator(coordinator_id: int) -> CoordinatorRecord | None:
    """Get a coordinator record by ID."""
    store = get_coordinators_db()
    return store.fetch_by_id(coordinator_id)


def get_coordinator_by_user(user: str) -> CoordinatorRecord | None:
    """Get a coordinator record by username."""
    store = get_coordinators_db()
    return store.fetch_by_user(user)


def add_coordinator(user: str, active: int = 1) -> CoordinatorRecord:
    """Add a new coordinator record."""
    store = get_coordinators_db()
    return store.add(user, active)


def add_or_update_coordinator(user: str, active: int = 1) -> CoordinatorRecord:
    """Add or update a coordinator record."""
    store = get_coordinators_db()
    return store.add_or_update(user, active)


def update_coordinator(coordinator_id: int, **kwargs) -> CoordinatorRecord:
    """Update a coordinator record."""
    store = get_coordinators_db()
    return store.update(coordinator_id, **kwargs)


def delete_coordinator(coordinator_id: int) -> CoordinatorRecord:
    """Delete a coordinator record by ID."""
    store = get_coordinators_db()
    return store.delete(coordinator_id)


def is_coordinator(user: str) -> bool:
    """Check if a user is a coordinator."""
    store = get_coordinators_db()
    record = store.fetch_by_user(user)
    return record is not None and record.active == 1


__all__ = [
    "get_coordinators_db",
    "list_coordinators",
    "list_active_coordinators",
    "get_coordinator",
    "get_coordinator_by_user",
    "add_coordinator",
    "add_or_update_coordinator",
    "update_coordinator",
    "delete_coordinator",
    "is_coordinator",
]
