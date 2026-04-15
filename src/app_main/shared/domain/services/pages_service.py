"""Utilities for managing pages and page targets."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ....config import settings
from ...db.db_pages import PageRecord, PagesDB
from ...services import has_db_config

logger = logging.getLogger(__name__)

_PAGE_STORE: PagesDB | None = None


def get_pages_db() -> PagesDB:
    global _PAGE_STORE

    if _PAGE_STORE is None:
        if not has_db_config():
            raise RuntimeError("PagesDB requires database configuration; no fallback store is available.")

        try:
            _PAGE_STORE = PagesDB(settings.database_data)
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


def find_exists_or_update(
    title: str,
    lang: str,
    user: str,
    target: str,
    use_user_sql: bool,
) -> bool:
    """Check if a page record exists and update target if empty."""

    store = get_pages_db()
    return store._find_exists_or_update(title, lang, user, target, use_user_sql)


def insert_page_target(
    sourcetitle: str,
    tr_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    table_name: str,
    mdwiki_revid: int | None = None,
    word: int = 0,
) -> dict[str, Any]:
    """Insert a page target record."""

    store = get_pages_db()
    return store.insert_page_target(
        sourcetitle=sourcetitle,
        tr_type=tr_type,
        cat=cat,
        lang=lang,
        user=user,
        target=target,
        table_name=table_name,
        mdwiki_revid=mdwiki_revid,
        word=word,
    )


__all__ = [
    "get_pages_db",
    "PageRecord",
    "PagesDB",
    "list_pages",
    "add_or_update_page",
    "add_page",
    "update_page",
    "delete_page",
    "find_exists_or_update",
    "insert_page_target",
]
