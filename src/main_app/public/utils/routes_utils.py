from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Dict

from ..auth.utils import load_user

logger = logging.getLogger(__name__)


def _is_admin(user: Any) -> bool:
    """Check if user is an active coordinator (admin)."""
    return bool(user and getattr(user, "is_active_admin", False))


def context_data(
    wiki_domain: str,
    static_server: str,
    tool_title: str = "",
) -> dict[str, Any]:
    """
    Used in @app.context_processor to inject variables into templates.
    """
    # Safe retrieval from g with a fallback to None
    user = load_user()

    username = user.username if user else None

    return {
        "is_authenticated": user is not None,
        "current_username": username,
        "is_admin": _is_admin(user),
        "wiki_domain": wiki_domain,
        "static_server": static_server,
        "tool_title": tool_title,
        "username": user.username if user else None,
        "yesterday": (date.today() - timedelta(days=1)).isoformat(),
    }


def load_auth_payload(user: Any | None) -> Dict[str, Any]:
    if user and hasattr(user, "to_auth_payload"):
        return user.to_auth_payload()
    if user:
        access_key, access_secret = user.access_token, user.access_secret
        return {
            "id": user.user_id,
            "username": user.username,
            "access_token": access_key,
            "access_secret": access_secret,
        }
    return {}


__all__ = [
    "context_data",
    "load_auth_payload",
]
