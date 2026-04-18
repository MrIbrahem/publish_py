"""Utilities for managing in_process records."""

from __future__ import annotations

import logging
from typing import List

from ....config import has_db_config, settings
from ..db.db_in_process import InProcessDB
from ..models import InProcessRecord

logger = logging.getLogger(__name__)

_IN_PROCESS_STORE: InProcessDB | None = None


def get_in_process_db() -> InProcessDB:
    global _IN_PROCESS_STORE

    if _IN_PROCESS_STORE is None:
        if not has_db_config():
            raise RuntimeError("InProcessDB requires database configuration; no fallback store is available.")

        try:
            _IN_PROCESS_STORE = InProcessDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL InProcessDB")
            raise RuntimeError("Unable to initialize InProcessDB") from exc

    return _IN_PROCESS_STORE


def list_in_process() -> List[InProcessRecord]:
    """Return all in_process records."""
    store = get_in_process_db()
    return store.list()


def list_in_process_by_user(user: str) -> List[InProcessRecord]:
    """Return in_process records for a specific user."""
    store = get_in_process_db()
    return store.list_by_user(user)


def list_in_process_by_lang(lang: str) -> List[InProcessRecord]:
    """Return in_process records for a specific language."""
    store = get_in_process_db()
    return store.list_by_lang(lang)


def get_in_process(process_id: int) -> InProcessRecord | None:
    """Get an in_process record by ID."""
    store = get_in_process_db()
    return store.fetch_by_id(process_id)


def get_in_process_by_title_user_lang(title: str, user: str, lang: str) -> InProcessRecord | None:
    """Get an in_process record by title, user, and language."""
    store = get_in_process_db()
    return store.fetch_by_title_user_lang(title, user, lang)


def add_in_process(
    title: str,
    user: str,
    lang: str,
    cat: str | None = "RTT",
    translate_type: str | None = "lead",
    word: int | None = 0,
) -> InProcessRecord:
    """Add a new in_process record."""
    store = get_in_process_db()
    return store.add(title, user, lang, cat, translate_type, word)


def update_in_process(process_id: int, **kwargs) -> InProcessRecord:
    """Update an in_process record."""
    store = get_in_process_db()
    return store.update(process_id, **kwargs)


def delete_in_process(process_id: int) -> InProcessRecord:
    """Delete an in_process record by ID."""
    store = get_in_process_db()
    return store.delete(process_id)


def delete_in_process_by_title_user_lang(title: str, user: str, lang: str) -> bool:
    """Delete an in_process record by title, user, and language."""
    store = get_in_process_db()
    return store.delete_by_title_user_lang(title, user, lang)


def is_in_process(title: str, user: str, lang: str) -> bool:
    """Check if a translation is in process."""
    store = get_in_process_db()
    record = store.fetch_by_title_user_lang(title, user, lang)
    return record is not None


__all__ = [
    "get_in_process_db",
    "list_in_process",
    "list_in_process_by_user",
    "list_in_process_by_lang",
    "get_in_process",
    "get_in_process_by_title_user_lang",
    "add_in_process",
    "update_in_process",
    "delete_in_process",
    "delete_in_process_by_title_user_lang",
    "is_in_process",
]
