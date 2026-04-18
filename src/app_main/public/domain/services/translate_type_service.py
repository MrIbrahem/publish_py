"""Utilities for managing translate_type."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ..db.db_translate_type import TranslateTypeDB
from ..models import TranslateTypeRecord

logger = logging.getLogger(__name__)

_TRANSLATE_TYPE_STORE: TranslateTypeDB | None = None


from ....config import has_db_config


def get_translate_type_db() -> TranslateTypeDB:
    global _TRANSLATE_TYPE_STORE

    if _TRANSLATE_TYPE_STORE is None:
        if not has_db_config():
            raise RuntimeError("TranslateTypeDB requires database configuration; no fallback store is available.")

        try:
            _TRANSLATE_TYPE_STORE = TranslateTypeDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL TranslateTypeDB")
            raise RuntimeError("Unable to initialize TranslateTypeDB") from exc

    return _TRANSLATE_TYPE_STORE


def list_translate_types() -> List[TranslateTypeRecord]:
    """Return all translate_type records."""
    store = get_translate_type_db()
    return store.list()


def list_lead_enabled_types() -> List[TranslateTypeRecord]:
    """Return translate_type records with lead enabled."""
    store = get_translate_type_db()
    return store.list_lead_enabled()


def list_full_enabled_types() -> List[TranslateTypeRecord]:
    """Return translate_type records with full enabled."""
    store = get_translate_type_db()
    return store.list_full_enabled()


def get_translate_type(tt_id: int) -> TranslateTypeRecord | None:
    """Get a translate_type record by ID."""
    store = get_translate_type_db()
    return store.fetch_by_id(tt_id)


def get_translate_type_by_title(title: str) -> TranslateTypeRecord | None:
    """Get a translate_type record by title."""
    store = get_translate_type_db()
    return store.fetch_by_title(title)


def add_translate_type(
    tt_title: str,
    tt_lead: int = 1,
    tt_full: int = 0,
) -> TranslateTypeRecord:
    """Add a new translate_type record."""
    store = get_translate_type_db()
    return store.add(tt_title, tt_lead, tt_full)


def add_or_update_translate_type(
    tt_title: str,
    tt_lead: int = 1,
    tt_full: int = 0,
) -> TranslateTypeRecord:
    """Add or update a translate_type record."""
    store = get_translate_type_db()
    return store.add_or_update(tt_title, tt_lead, tt_full)


def update_translate_type(tt_id: int, **kwargs) -> TranslateTypeRecord:
    """Update a translate_type record."""
    store = get_translate_type_db()
    return store.update(tt_id, **kwargs)


def delete_translate_type(tt_id: int) -> TranslateTypeRecord:
    """Delete a translate_type record by ID."""
    store = get_translate_type_db()
    return store.delete(tt_id)


def can_translate_lead(title: str) -> bool:
    """Check if a title can be translated as lead."""
    store = get_translate_type_db()
    record = store.fetch_by_title(title)
    return record.tt_lead == 1 if record else True


def can_translate_full(title: str) -> bool:
    """Check if a title can be translated as full."""
    store = get_translate_type_db()
    record = store.fetch_by_title(title)
    return record.tt_full == 1 if record else False


__all__ = [
    "get_translate_type_db",
    "list_translate_types",
    "list_lead_enabled_types",
    "list_full_enabled_types",
    "get_translate_type",
    "get_translate_type_by_title",
    "add_translate_type",
    "add_or_update_translate_type",
    "update_translate_type",
    "delete_translate_type",
    "can_translate_lead",
    "can_translate_full",
]
