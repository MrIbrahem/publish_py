"""
Persistence helpers for storing encrypted OAuth tokens.
"""

from __future__ import annotations

import logging
from typing import Optional

from ....config import settings
from ..db.db_user_tokens import UserTokenDB
from ..models.user_token import UserTokenRecord
from .db_service import has_db_config

logger = logging.getLogger(__name__)

_user_db: UserTokenDB | None = None


def get_store() -> UserTokenDB:
    global _user_db

    if _user_db is None:
        if not has_db_config():
            raise RuntimeError("UserTokenDB requires database configuration; no fallback store is available.")

        try:
            _user_db = UserTokenDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize UserTokenDB")
            raise RuntimeError("Unable to initialize UserTokenDB") from exc

    return _user_db


def upsert_user_token(*, user_id: int, username: str, access_key: str, access_secret: str) -> None:
    """Insert or update the encrypted OAuth credentials for a user."""

    store = get_store()
    return store.upsert(user_id, username, access_key, access_secret)


def get_user_token(user_id: str | int) -> Optional[UserTokenRecord]:
    """Fetch the encrypted OAuth credentials for a user."""

    if not user_id:
        return None

    store = get_store()
    try:
        return store._fetch_by_id(user_id)
    except LookupError:
        return None


def delete_user_token(user_id: int) -> None:
    """Remove the stored OAuth credentials for the given user id."""

    if not user_id:
        return None

    store = get_store()
    store.delete(user_id)


def get_user_token_by_username(username: str) -> Optional[UserTokenRecord]:
    """Fetch the encrypted OAuth credentials for a user by username.

    This mirrors the PHP access_helps.php get_access_from_db() function.

    Args:
        username: The username to look up

    Returns:
        UserTokenRecord if found, None otherwise

    """
    username = username.strip()

    if not username:
        return None

    store = get_store()
    try:
        return store._fetch_by_username(username)
    except LookupError:
        return None


def delete_user_token_by_username(username: str) -> None:
    """Remove the stored OAuth credentials for the given username.

    This mirrors the PHP access_helps.php del_access_from_db() function.

    Args:
        username: The username to delete credentials for
    """
    username = username.strip()

    if not username:
        return None

    store = get_store()

    user_id = store.get_user_id(username)
    if user_id:
        store.delete(user_id)
