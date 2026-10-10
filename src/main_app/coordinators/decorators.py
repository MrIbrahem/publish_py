"""Coordinator-only routes for managing coordinator access."""

from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from typing import TypeVar, cast

from flask import (
    abort,
    redirect,
    url_for,
)
from flask.typing import ResponseReturnValue

from ..services.auth.current_user import CurrentUser
from ..services.auth.utils import get_current_user

logger = logging.getLogger(__name__)

FuncType = TypeVar("FuncType", bound=Callable[..., ResponseReturnValue])


def coordinator_required(view: FuncType) -> FuncType:  # noqa: UP047
    """Decorator enforcing that the current user is an coordinatoristrator."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        user: CurrentUser | None = get_current_user()
        if not user:
            return redirect(url_for("auth.login"))
        if not user.is_active_coordinator:
            logger.warning("User %s tried to access coordinator-only route", user.username)
            abort(403)
        return view(*args, **kwargs)

    return cast(FuncType, wrapped)


def coordinator_guard() -> ResponseReturnValue | None:
    """Blueprint-level guard rejecting any non-coordinator request to the coordinator area.

    Applies the same checks as :func:`coordinator_required` but as a ``before_request``
    hook, so it covers every endpoint registered under the coordinator blueprint —
    including the nested sub-blueprints — even when a view forgets the decorator.
    """
    user: CurrentUser | None = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
    if not user.is_active_coordinator:
        logger.warning("User %s tried to access coordinator-only route", user.username)
        abort(403)
    return None


__all__ = [
    "coordinator_guard",
    "coordinator_required",
]
