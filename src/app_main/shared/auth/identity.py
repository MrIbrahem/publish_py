"""Helpers for loading the current authenticated user."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from flask import g, request, session

from ..core.cookies.cookie import extract_user_id
from ...config import settings
from ..domain.services.users_services import UserTokenRecord, get_user_token


@dataclass(frozen=True)
class CurrentUser:
    """Lightweight representation of the authenticated user."""

    user_id: str
    username: str


def _resolve_user_id() -> Optional[int]:
    uid = session.get("uid")
    if isinstance(uid, int):
        return uid
    try:
        return int(uid) if uid is not None else None
    except (TypeError, ValueError):
        return None


def current_user() -> Optional[UserTokenRecord]:
    if hasattr(g, "_current_user"):
        return g._current_user  # type: ignore[attr-defined]

    user_id = _resolve_user_id()
    if user_id is None:
        signed = request.cookies.get(settings.cookie.name)
        if signed:
            user_id = extract_user_id(signed)
            if user_id is not None:
                session["uid"] = user_id

    user = get_user_token(user_id) if user_id is not None else None
    if user and session.get("username") != user.username:
        session["username"] = user.username

    g._current_user = user  # type: ignore[attr-defined]
    return user


__all__ = [
    "CurrentUser",
    "current_user",
]
