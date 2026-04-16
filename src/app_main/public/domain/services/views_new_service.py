"""Utilities for managing views_new."""

from __future__ import annotations

import logging
from typing import List

from ....config import settings
from ....shared.domain.services.db_service import has_db_config
from ..db.db_views_new import ViewsNewDB
from ..models.views_new import ViewsNewRecord

logger = logging.getLogger(__name__)

_VIEWS_NEW_STORE: ViewsNewDB | None = None


def get_views_new_db() -> ViewsNewDB:
    global _VIEWS_NEW_STORE

    if _VIEWS_NEW_STORE is None:
        if not has_db_config():
            raise RuntimeError("ViewsNewDB requires database configuration; no fallback store is available.")

        try:
            _VIEWS_NEW_STORE = ViewsNewDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL ViewsNewDB")
            raise RuntimeError("Unable to initialize ViewsNewDB") from exc

    return _VIEWS_NEW_STORE


def list_views_new() -> List[ViewsNewRecord]:
    """Return all views_new records."""
    store = get_views_new_db()
    return store.list()


def list_views_by_target(target: str) -> List[ViewsNewRecord]:
    """Return views_new records for a specific target."""
    store = get_views_new_db()
    return store.list_by_target(target)


def list_views_by_lang(lang: str) -> List[ViewsNewRecord]:
    """Return views_new records for a specific language."""
    store = get_views_new_db()
    return store.list_by_lang(lang)


def get_views_new(view_id: int) -> ViewsNewRecord | None:
    """Get a views_new record by ID."""
    store = get_views_new_db()
    return store.fetch_by_id(view_id)


def get_views_by_target_lang_year(target: str, lang: str, year: int) -> ViewsNewRecord | None:
    """Get a views_new record by target, language, and year."""
    store = get_views_new_db()
    return store.fetch_by_target_lang_year(target, lang, year)


def add_views_new(
    target: str,
    lang: str,
    year: int,
    views: int | None = 0,
) -> ViewsNewRecord:
    """Add a new views_new record."""
    store = get_views_new_db()
    return store.add(target, lang, year, views)


def add_or_update_views_new(
    target: str,
    lang: str,
    year: int,
    views: int | None = 0,
) -> ViewsNewRecord:
    """Add or update a views_new record."""
    store = get_views_new_db()
    return store.add_or_update(target, lang, year, views)


def update_views_new(view_id: int, **kwargs) -> ViewsNewRecord:
    """Update a views_new record."""
    store = get_views_new_db()
    return store.update(view_id, **kwargs)


def delete_views_new(view_id: int) -> ViewsNewRecord:
    """Delete a views_new record by ID."""
    store = get_views_new_db()
    return store.delete(view_id)


def get_total_views_for_target(target: str) -> int:
    """Get total views across all years for a target."""
    store = get_views_new_db()
    records = store.list_by_target(target)
    return sum(r.views or 0 for r in records)


__all__ = [
    "get_views_new_db",
    "list_views_new",
    "list_views_by_target",
    "list_views_by_lang",
    "get_views_new",
    "get_views_by_target_lang_year",
    "add_views_new",
    "add_or_update_views_new",
    "update_views_new",
    "delete_views_new",
    "get_total_views_for_target",
]
