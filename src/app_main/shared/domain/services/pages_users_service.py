"""Utilities for managing pages_users and user_page targets."""

from __future__ import annotations

import logging
from typing import Any, List

from ....config import settings
from ..db.db_pages_users import UserPagesDB
from ..models.user_page import UserPageRecord
from .db_service import has_db_config

logger = logging.getLogger(__name__)

_USER_PAGE_STORE: UserPagesDB | None = None


def get_pages_db() -> UserPagesDB:
    global _USER_PAGE_STORE

    if _USER_PAGE_STORE is None:
        if not has_db_config():
            raise RuntimeError("UserPagesDB requires database configuration; no fallback store is available.")

        try:
            _USER_PAGE_STORE = UserPagesDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL page store")
            raise RuntimeError("Unable to initialize page store") from exc

    return _USER_PAGE_STORE


def list_pages() -> List[UserPageRecord]:
    """Return all pages_users while keeping settings.admins in sync."""

    store = get_pages_db()

    coords = store.list()
    return coords


def add_page(title: str, main_file: str) -> UserPageRecord:
    """Add a page."""

    store = get_pages_db()
    record = store.add(title, main_file)

    return record


def add_or_update_page(title: str, main_file: str) -> UserPageRecord:
    """Add a page."""

    store = get_pages_db()
    record = store.add_or_update(title, main_file)

    return record


def update_page(page_id: int, title: str, main_file: str) -> UserPageRecord:
    """Update page."""

    store = get_pages_db()
    record = store.update(page_id, title, main_file)

    return record


def delete_page(page_id: int) -> UserPageRecord:
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
    """Check if a user_page record exists and update target if empty."""

    store = get_pages_db()
    return store._find_exists_or_update(title, lang, user, target, use_user_sql)


def insert_user_page_target(
    sourcetitle: str,
    tr_type: str,
    cat: str,
    lang: str,
    user: str,
    target: str,
    mdwiki_revid: int | None = None,
    word: int = 0,
) -> dict[str, Any]:
    """Insert a user_page target record."""

    store = get_pages_db()
    return store.insert_page_target(
        sourcetitle=sourcetitle,
        tr_type=tr_type,
        cat=cat,
        lang=lang,
        user=user,
        target=target,
        mdwiki_revid=mdwiki_revid,
        word=word,
    )


__all__ = [
    "get_pages_db",
    "list_pages",
    "add_or_update_page",
    "add_page",
    "update_page",
    "delete_page",
    "find_exists_or_update",
    "insert_user_page_target",
]
