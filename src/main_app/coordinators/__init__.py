"""Coordinator blueprint package."""

from __future__ import annotations

from flask import Blueprint, Flask

from .coordinator_panel import CoordinatorPanel
from .decorators import coordinator_guard
from .routes import CoordinatorRouteRegister


def register_bp_coordinators_blueprints(app: Flask) -> None:
    bp_coordinators = Blueprint("coordinators_panel", __name__, url_prefix="/coordinators_panel")
    # Reject every request to /coordinators_panel unless it comes from an active admin.
    # Flask propagates a parent blueprint's before_request to nested child
    # blueprints, so this single guard covers every admin sub-blueprint too.
    bp_coordinators.before_request(coordinator_guard)
    CoordinatorPanel().register(bp_coordinators)
    CoordinatorRouteRegister.register(bp_coordinators)
    app.register_blueprint(bp_coordinators)


__all__ = [
    "register_bp_coordinators_blueprints",
]
