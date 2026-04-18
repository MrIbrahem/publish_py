"""Utilities for managing enwiki pageviews."""

from __future__ import annotations

import logging
from typing import List

from ....config import has_db_config, settings
from ..db.db_enwiki_pageviews import EnwikiPageviewsDB
from .....db_models.public_models import EnwikiPageviewRecord

logger = logging.getLogger(__name__)

_ENWIKI_PAGEVIEWS_STORE: EnwikiPageviewsDB | None = None


def get_enwiki_pageviews_db() -> EnwikiPageviewsDB:
    global _ENWIKI_PAGEVIEWS_STORE

    if _ENWIKI_PAGEVIEWS_STORE is None:
        if not has_db_config():
            raise RuntimeError("EnwikiPageviewsDB requires database configuration; no fallback store is available.")

        try:
            _ENWIKI_PAGEVIEWS_STORE = EnwikiPageviewsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL EnwikiPageviewsDB")
            raise RuntimeError("Unable to initialize EnwikiPageviewsDB") from exc

    return _ENWIKI_PAGEVIEWS_STORE


def list_enwiki_pageviews() -> List[EnwikiPageviewRecord]:
    """Return all enwiki pageview records."""
    store = get_enwiki_pageviews_db()
    return store.list()


def get_top_enwiki_pageviews(limit: int = 100) -> List[EnwikiPageviewRecord]:
    """Return top enwiki pageview records by view count."""
    store = get_enwiki_pageviews_db()
    return store.list_by_views(limit)


def get_enwiki_pageview(pageview_id: int) -> EnwikiPageviewRecord | None:
    """Get an enwiki pageview record by ID."""
    store = get_enwiki_pageviews_db()
    return store.fetch_by_id(pageview_id)


def get_enwiki_pageview_by_title(title: str) -> EnwikiPageviewRecord | None:
    """Get an enwiki pageview record by title."""
    store = get_enwiki_pageviews_db()
    return store.fetch_by_title(title)


def add_enwiki_pageview(title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
    """Add a new enwiki pageview record."""
    store = get_enwiki_pageviews_db()
    return store.add(title, en_views)


def add_or_update_enwiki_pageview(title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
    """Add or update an enwiki pageview record."""
    store = get_enwiki_pageviews_db()
    return store.add_or_update(title, en_views)


def update_enwiki_pageview(pageview_id: int, **kwargs) -> EnwikiPageviewRecord:
    """Update an enwiki pageview record."""
    store = get_enwiki_pageviews_db()
    return store.update(pageview_id, **kwargs)


def delete_enwiki_pageview(pageview_id: int) -> EnwikiPageviewRecord:
    """Delete an enwiki pageview record by ID."""
    store = get_enwiki_pageviews_db()
    return store.delete(pageview_id)


__all__ = [
    "get_enwiki_pageviews_db",
    "list_enwiki_pageviews",
    "get_top_enwiki_pageviews",
    "get_enwiki_pageview",
    "get_enwiki_pageview_by_title",
    "add_enwiki_pageview",
    "add_or_update_enwiki_pageview",
    "update_enwiki_pageview",
    "delete_enwiki_pageview",
]
