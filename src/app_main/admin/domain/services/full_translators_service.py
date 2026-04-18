"""Utilities for managing full translators."""

from __future__ import annotations

import logging
from typing import List

from ....config import has_db_config, settings
from ..db.db_full_translators import FullTranslatorsDB
from ..models import FullTranslatorRecord

logger = logging.getLogger(__name__)

_FULL_TRANSLATORS_STORE: FullTranslatorsDB | None = None


def get_full_translators_db() -> FullTranslatorsDB:
    global _FULL_TRANSLATORS_STORE

    if _FULL_TRANSLATORS_STORE is None:
        if not has_db_config():
            raise RuntimeError("FullTranslatorsDB requires database configuration; no fallback store is available.")

        try:
            _FULL_TRANSLATORS_STORE = FullTranslatorsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL FullTranslatorsDB")
            raise RuntimeError("Unable to initialize FullTranslatorsDB") from exc

    return _FULL_TRANSLATORS_STORE


def list_full_translators() -> List[FullTranslatorRecord]:
    """Return all full translator records."""
    store = get_full_translators_db()
    return store.list()


def list_active_full_translators() -> List[FullTranslatorRecord]:
    """Return all active full translator records."""
    store = get_full_translators_db()
    return store.list_active()


def get_full_translator(translator_id: int) -> FullTranslatorRecord | None:
    """Get a full translator record by ID."""
    store = get_full_translators_db()
    return store.fetch_by_id(translator_id)


def get_full_translator_by_user(user: str) -> FullTranslatorRecord | None:
    """Get a full translator record by username."""
    store = get_full_translators_db()
    return store.fetch_by_user(user)


def add_full_translator(user: str, active: int = 1) -> FullTranslatorRecord:
    """Add a new full translator record."""
    store = get_full_translators_db()
    return store.add(user, active)


def add_or_update_full_translator(user: str, active: int = 1) -> FullTranslatorRecord:
    """Add or update a full translator record."""
    store = get_full_translators_db()
    return store.add_or_update(user, active)


def update_full_translator(translator_id: int, **kwargs) -> FullTranslatorRecord:
    """Update a full translator record."""
    store = get_full_translators_db()
    return store.update(translator_id, **kwargs)


def delete_full_translator(translator_id: int) -> FullTranslatorRecord:
    """Delete a full translator record by ID."""
    store = get_full_translators_db()
    return store.delete(translator_id)


def is_full_translator(user: str) -> bool:
    """Check if a user is a full translator."""
    store = get_full_translators_db()
    record = store.fetch_by_user(user)
    return record is not None and record.active == 1


__all__ = [
    "get_full_translators_db",
    "list_full_translators",
    "list_active_full_translators",
    "get_full_translator",
    "get_full_translator_by_user",
    "add_full_translator",
    "add_or_update_full_translator",
    "update_full_translator",
    "delete_full_translator",
    "is_full_translator",
]
