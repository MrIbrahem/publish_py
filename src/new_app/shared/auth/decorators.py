"""
Auth decorators
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast

from flask import redirect, request, session, url_for

from ....app_main.config import settings

from .identity import current_user

F = TypeVar("F", bound=Callable[..., Any])


def oauth_required(func: F) -> F:
    """Decorator that requires a full OAuth credential bundle."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        if settings.oauth and settings.oauth.enabled and not current_user():
            session["post_login_redirect"] = request.url
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return cast(F, wrapper)


__all__ = [
    "oauth_required",
]
