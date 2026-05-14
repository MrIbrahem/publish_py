"""Admin-only routes for managing coordinator access."""

from __future__ import annotations

from functools import wraps
from typing import Callable, List, TypeVar, cast

from flask import (
    abort,
    g,
    redirect,
    url_for,
)
from flask.typing import ResponseReturnValue

from ..shared.auth.identity import current_user
from ..shared.services.coordinator_service import active_coordinators

F = TypeVar("F", bound=Callable[..., ResponseReturnValue])


def _get_cached_active_coordinators() -> List[str]:
    """Get active coordinators, cached for the duration of the request."""
    if hasattr(g, "_active_coordinators"):
        return g._active_coordinators  # type: ignore[attr-defined]

    coordinators = active_coordinators()
    g._active_coordinators = coordinators  # type: ignore[attr-defined]
    return coordinators


def admin_required(view: F) -> F:  # noqa: UP047
    """Decorator enforcing that the current user is an administrator."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            return redirect(url_for("auth.login"))
        if user.username not in _get_cached_active_coordinators():
            abort(403)
        return view(*args, **kwargs)

    return cast(F, wrapped)
