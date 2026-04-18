""" """

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue

from ..sqlalchemy_db.services.coordinator_service import (
    list_coordinators,
    add_coordinator,
    set_coordinator_active,
    delete_coordinator,
)
from .decorators import admin_required

logger = logging.getLogger(__name__)


def _coordinators_dashboard():
    """Render the coordinator management dashboard."""

    coordinators = list_coordinators()
    total = len(coordinators)
    is_active = sum(1 for coord in coordinators if coord.is_active)

    return render_template(
        "admins/coordinators.html",
        coordinators=coordinators,
        total_coordinators=total,
        active_coordinators=is_active,
        inactive_coordinators=total - is_active,
    )


def _add_coordinator() -> ResponseReturnValue:
    """Create a new coordinator from the submitted username."""

    username = request.form.get("username", "").strip()
    if not username:
        flash("Username is required to add a coordinator.", "danger")
        return redirect(url_for("admin.coordinators_dashboard"))

    try:
        record = add_coordinator(username)
    except (LookupError, ValueError) as exc:
        logger.exception("Unable to Add coordinator.")
        flash(str(exc), "warning")
    except Exception:  # pragma: no cover - defensive guard
        logger.exception("Unable to add coordinator.")
        flash("Unable to add coordinator. Please try again.", "danger")
    else:
        flash(f"Coordinator '{record.username}' added.", "success")

    return redirect(url_for("admin.coordinators_dashboard"))


def _update_coordinator_active(coordinator_id: int) -> ResponseReturnValue:
    """Toggle the active flag for a coordinator."""

    desired = request.form.get("is_active", "0") == "1"
    try:
        record = set_coordinator_active(coordinator_id, desired)
    except LookupError as exc:
        logger.exception("Unable to update coordinator.")
        flash(str(exc), "warning")
    except Exception:  # pragma: no cover - defensive guard
        logger.exception("Unable to update coordinator.")
        flash("Unable to update coordinator status. Please try again.", "danger")
    else:
        state = "activated" if record.is_active else "deactivated"
        flash(f"Coordinator '{record.username}' {state}.", "success")

    return redirect(url_for("admin.coordinators_dashboard"))


def _delete_coordinator(coordinator_id: int) -> ResponseReturnValue:
    """Remove a coordinator entirely."""

    try:
        record = delete_coordinator(coordinator_id)
    except LookupError as exc:
        logger.exception("Unable to delete coordinator.")
        flash(str(exc), "warning")
    except Exception:  # pragma: no cover - defensive guard
        logger.exception("Unable to delete coordinator.")
        flash("Unable to delete coordinator. Please try again.", "danger")
    else:
        flash(f"Coordinator '{record.username}' removed.", "success")

    return redirect(url_for("admin.coordinators_dashboard"))


class Coordinators:
    def __init__(self, bp_admin: Blueprint):
        @bp_admin.get("/coordinators")
        @admin_required
        def coordinators_dashboard():
            return _coordinators_dashboard()

        @bp_admin.post("/coordinators/add")
        @admin_required
        def add_coordinator() -> ResponseReturnValue:
            return _add_coordinator()

        @bp_admin.post("/coordinators/<int:coordinator_id>/active")
        @admin_required
        def update_coordinator_active(coordinator_id: int) -> ResponseReturnValue:
            return _update_coordinator_active(coordinator_id)

        @bp_admin.post("/coordinators/<int:coordinator_id>/delete")
        @admin_required
        def delete_coordinator(coordinator_id: int) -> ResponseReturnValue:
            return _delete_coordinator(coordinator_id)
