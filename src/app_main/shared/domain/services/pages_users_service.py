"""Utilities for managing pages_users and user_page targets."""

from __future__ import annotations

import logging
from typing import Any, List

from ....config import has_db_config, settings
from ..db.db_pages_users import UserPagesDB
from .....db_models.shared_models import UserPageRecord

logger = logging.getLogger(__name__)

_USER_PAGE_STORE: UserPagesDB | None = None


def get_user_pages_db() -> UserPagesDB:
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


def list_user_pages() -> List[UserPageRecord]:
    """Return all pages_users records."""

    store = get_user_pages_db()

    pages = store.list()
    return pages


def add_user_page(title: str, main_file: str) -> UserPageRecord:
    """Add a page."""

    store = get_user_pages_db()
    record = store.add(title, main_file)

    return record


def add_or_update_user_page(title: str, main_file: str) -> UserPageRecord:
    """Add a page."""

    store = get_user_pages_db()
    record = store.add_or_update(title, main_file)

    return record


def update_user_page(page_id: int, title: str, main_file: str) -> UserPageRecord:
    """Update page."""

    store = get_user_pages_db()
    record = store.update(page_id, title, main_file)

    return record


def delete_user_page(page_id: int) -> UserPageRecord:
    """Delete a page."""

    store = get_user_pages_db()
    record = store.delete(page_id)

    return record


def find_exists_or_update_user_page(
    title: str,
    lang: str,
    user: str,
    target: str,
) -> bool:
    """Check if a user_page record exists and update target if empty."""

    store = get_user_pages_db()
    return store._find_exists_or_update(title, lang, user, target)


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

    store = get_user_pages_db()
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
    "list_user_pages",
    "add_or_update_user_page",
    "add_user_page",
    "update_user_page",
    "delete_user_page",
    "find_exists_or_update_user_page",
    "insert_user_page_target",
]
