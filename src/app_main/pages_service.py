"""Utilities for managing administrator (page) accounts."""

from __future__ import annotations

import logging
from typing import List

from .config import settings
from .db import has_db_config
from .db.db_Pages import PageRecord, PagesDB

logger = logging.getLogger(__name__)

_PAGE_STORE: PagesDB | None = None


def get_pages_db() -> PagesDB:
    global _PAGE_STORE

    if _PAGE_STORE is None:
        if not has_db_config():
            raise RuntimeError(
                "Template administration requires database configuration; no fallback store is available."
            )

        try:
            _PAGE_STORE = PagesDB(settings.db_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL page store")
            raise RuntimeError("Unable to initialize page store") from exc

    return _PAGE_STORE


def list_pages() -> List[PageRecord]:
    """Return all pages while keeping settings.admins in sync."""

    store = get_pages_db()

    coords = store.list()
    return coords


def add_page(title: str, main_file: str) -> PageRecord:
    """Add a page."""

    store = get_pages_db()
    record = store.add(title, main_file)

    return record


def add_or_update_page(title: str, main_file: str) -> PageRecord:
    """Add a page."""

    store = get_pages_db()
    record = store.add_or_update(title, main_file)

    return record


def update_page(page_id: int, title: str, main_file: str) -> PageRecord:
    """Update page."""

    store = get_pages_db()
    record = store.update(page_id, title, main_file)

    return record


def delete_page(page_id: int) -> PageRecord:
    """Delete a page."""

    store = get_pages_db()
    record = store.delete(page_id)

    return record


__all__ = [
    "get_pages_db",
    "PageRecord",
    "PagesDB",
    "list_pages",
    "add_or_update_page",
    "add_page",
    "update_page",
    "delete_page",
]
