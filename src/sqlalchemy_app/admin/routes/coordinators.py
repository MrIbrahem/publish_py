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

from ..decorators import admin_required
from ..sqlalchemy_db.services.coordinator_service import (
    add_coordinator,
    delete_coordinator,
    list_coordinators,
    set_coordinator_active,
)

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


def _set_record_active_status(record_id: int, is_active: bool) -> ResponseReturnValue:
    """Shared helper to update coordinator active status."""
    action = "activate" if is_active else "deactivate"
    past_tense = "activated" if is_active else "deactivated"
    try:
        record = set_coordinator_active(record_id, is_active)
    except LookupError as exc:
        logger.exception(f"Unable to {action} coordinator.")
        flash(str(exc), "warning")
    except Exception:  # pragma: no cover - defensive guard
        logger.exception(f"Unable to {action} coordinator.")
        flash(f"Unable to {action} coordinator. Please try again.", "danger")
    else:
        flash(f"Coordinator '{record.username}' {past_tense}.", "success")

    return redirect(url_for("admin.coordinators_dashboard"))


def _activate_record(record_id: int) -> ResponseReturnValue:
    """Activate a coordinator."""
    return _set_record_active_status(record_id, True)


def _deactivate_record(record_id: int) -> ResponseReturnValue:
    """Deactivate a coordinator."""
    return _set_record_active_status(record_id, False)


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
        flash(f"Coordinator '{coordinator_id}' removed.", "success")

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

        @bp_admin.post("/coordinators/<int:coordinator_id>/delete")
        @admin_required
        def delete_coordinator(coordinator_id: int) -> ResponseReturnValue:
            return _delete_coordinator(coordinator_id)

        @bp_admin.post("/coordinators/<int:record_id>/activate")
        @admin_required
        def activate_coordinator(record_id: int) -> ResponseReturnValue:
            return _activate_record(record_id)

        @bp_admin.post("/coordinators/<int:record_id>/deactivate")
        @admin_required
        def deactivate_coordinator(record_id: int) -> ResponseReturnValue:
            return _deactivate_record(record_id)
