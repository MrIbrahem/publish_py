"""Helpers for loading the current authenticated user."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from flask import g, request, session

from ...config import settings
from ...db.services.users import (
    get_user_token,
    is_active_coordinator,
    should_bypass_coordinator_check,
)
from ..core.cookies.cookie import extract_user_id


@dataclass(frozen=True)
class CurrentUser:
    """Bundles user identity and OAuth credentials
    Stored in ``g._current_user`` during the request lifecycle.
    """

    user_id: int
    username: str
    access_token: bytes = field(repr=False)
    access_secret: bytes = field(repr=False)
    is_active_admin: bool = False

    def to_auth_payload(self) -> dict[str, int | str | bytes]:
        return {
            "id": self.user_id,
            "username": self.username,
            "access_token": self.access_token,
            "access_secret": self.access_secret,
        }


def _resolve_user_id() -> Optional[int]:
    uid = session.get("uid")
    if isinstance(uid, int):
        return uid
    try:
        return int(uid) if uid is not None else None
    except (TypeError, ValueError):
        return None


def current_user() -> Optional[CurrentUser]:
    if hasattr(g, "_current_user"):
        return g._current_user  # type: ignore[attr-defined]

    if should_bypass_coordinator_check("BYPASS_ADMIN"):
        user = CurrentUser(
            user_id=0,
            username="BYPASS_ADMIN",
            access_token=b"bypass",
            access_secret=b"bypass",
            is_active_admin=True,
        )
        g._current_user = user
        return user

    user_id = _resolve_user_id()
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


__all__ = [
    "CurrentUser",
    "current_user",
]
