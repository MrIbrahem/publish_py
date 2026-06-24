"""
Authentication utilities and decorators for routes.
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from flask import g, redirect, request, session, url_for

from ...config import settings
from ...db.services.users import (
    get_user_token,
    is_active_coordinator,
)
from ...shared.auth.current_user import CurrentUser
from ...shared.core.cookies import extract_user_id

FuncType = TypeVar("FuncType", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


def load_user():
    user = getattr(g, "_current_user", None)
    return user


def _resolve_user_id(uid) -> int | None:
    if isinstance(uid, int):
        return uid
    try:
        return int(uid) if uid is not None else None
    except (TypeError, ValueError):
        return None


def load_logged_in_user() -> Optional[CurrentUser]:
    if hasattr(g, "_current_user"):
        return g._current_user  # type: ignore[attr-defined]

    uid = session.get("uid")
    user_id = _resolve_user_id(uid)
    if user_id is None:
        signed = request.cookies.get(settings.cookie.name)
        if signed:
            user_id = extract_user_id(signed)
            if user_id is not None:
                session["uid"] = user_id

    record = get_user_token(user_id) if user_id is not None else None
    if record is None:
        return None

    if session.get("username") != record.username:
        session["username"] = record.username

    user = CurrentUser(
        user_id=record.user_id,
        username=record.username,
        access_token=record.access_token,
        access_secret=record.access_secret,
        is_active_admin=is_active_coordinator(record.username),
    )

    g._current_user = user  # type: ignore[attr-defined]
    return user


def oauth_required(func: FuncType) -> FuncType:  # noqa: UP047
    """Decorator that requires a full OAuth credential bundle."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        if settings.oauth and not load_logged_in_user():
            session["post_login_redirect"] = request.url
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return cast(FuncType, wrapper)


__all__ = [
    "oauth_required",
]


__all__ = []
