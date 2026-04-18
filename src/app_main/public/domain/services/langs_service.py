"""Utilities for managing languages."""

from __future__ import annotations

import logging
from typing import List

from ....config import has_db_config, settings
from ..db.db_langs import LangsDB
from .....db_models.public_models import LangRecord

logger = logging.getLogger(__name__)

_LANGS_STORE: LangsDB | None = None


def get_langs_db() -> LangsDB:
    global _LANGS_STORE

    if _LANGS_STORE is None:
        if not has_db_config():
            raise RuntimeError("LangsDB requires database configuration; no fallback store is available.")

        try:
            _LANGS_STORE = LangsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL LangsDB")
            raise RuntimeError("Unable to initialize LangsDB") from exc

    return _LANGS_STORE


def list_langs() -> List[LangRecord]:
    """Return all language records."""
    store = get_langs_db()
    return store.list()


def get_lang(lang_id: int) -> LangRecord | None:
    """Get a language record by ID."""
    store = get_langs_db()
    return store.fetch_by_id(lang_id)


def get_lang_by_code(code: str) -> LangRecord | None:
    """Get a language record by code."""
    store = get_langs_db()
    return store.fetch_by_code(code)


def add_lang(code: str, autonym: str, name: str) -> LangRecord:
    """Add a new language record."""
    store = get_langs_db()
    return store.add(code, autonym, name)


def add_or_update_lang(code: str, autonym: str, name: str) -> LangRecord:
    """Add or update a language record."""
    store = get_langs_db()
    return store.add_or_update(code, autonym, name)


def update_lang(lang_id: int, **kwargs) -> LangRecord:
    """Update a language record."""
    store = get_langs_db()
    return store.update(lang_id, **kwargs)


def delete_lang(lang_id: int) -> LangRecord:
    """Delete a language record by ID."""
    store = get_langs_db()
    return store.delete(lang_id)


__all__ = [
    "get_langs_db",
    "list_langs",
    "get_lang",
    "get_lang_by_code",
    "add_lang",
    "add_or_update_lang",
    "update_lang",
    "delete_lang",
]
