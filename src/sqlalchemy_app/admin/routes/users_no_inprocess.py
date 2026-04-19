"""Admin-only routes for managing users not in process."""

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
from ..sqlalchemy_db.services.users_no_inprocess_service import (
    add_users_no_inprocess,
    delete_users_no_inprocess,
    list_users_no_inprocess,
    update_users_no_inprocess,
)

logger = logging.getLogger(__name__)


def _users_no_inprocess_dashboard():
    """Render the users not in process management dashboard."""

    users = list_users_no_inprocess()
    total = len(users)
    is_active = sum(1 for u in users if u.active)

    return render_template(
        "admins/users_no_inprocess.html",
        users=users,
        total_users=total,
        active_users=is_active,
        inactive_users=total - is_active,
    )


def _add_user_no_inprocess() -> ResponseReturnValue:
    """Create a new user not in process record from the submitted username."""

    username = request.form.get("username", "").strip()
    if not username:
        flash("Username is required to add a user.", "danger")
        return redirect(url_for("admin.users_no_inprocess_dashboard"))

    try:
        record = add_users_no_inprocess(username)
    except ValueError as exc:
        logger.warning(f"Unable to add user: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to add user.")
        flash("Unable to add user. Please try again.", "danger")
    else:
        flash(f"User '{record.user}' added to 'not in process' list.", "success")

    return redirect(url_for("admin.users_no_inprocess_dashboard"))


def _set_record_active_status(record_id: int, is_active: bool) -> ResponseReturnValue:
    """Shared helper to update record active status."""
    action = "activate" if is_active else "deactivate"
    past_tense = "activated" if is_active else "deactivated"
    try:
        record = update_users_no_inprocess(record_id, is_active)
    except LookupError as exc:
        logger.exception(f"Unable to {action} coordinator.")
        flash(str(exc), "warning")
    except Exception:  # pragma: no cover - defensive guard
        logger.exception(f"Unable to {action} record.")
        flash(f"Unable to {action} record. Please try again.", "danger")
    else:
        flash(f"Record '{record.username}' {past_tense}.", "success")

    return redirect(url_for("admin.users_no_inprocess_dashboard"))


def _activate_record(record_id: int) -> ResponseReturnValue:
    """Activate a record."""
    return _set_record_active_status(record_id, True)


def _deactivate_record(record_id: int) -> ResponseReturnValue:
    """Deactivate a record."""
    return _set_record_active_status(record_id, False)


def _delete_user_no_inprocess(record_id: int) -> ResponseReturnValue:
    """Remove a user not in process record entirely."""

    try:
        record = delete_users_no_inprocess(record_id)
    except ValueError as exc:
        logger.warning(f"Unable to delete user: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to delete user.")
        flash("Unable to delete user. Please try again.", "danger")
    else:
        flash(f"User '{record.user}' removed from 'not in process' list.", "success")

    return redirect(url_for("admin.users_no_inprocess_dashboard"))


class UsersNoInprocess:
    def __init__(self, bp_admin: Blueprint):
        @bp_admin.get("/users_no_inprocess")
        @admin_required
        def users_no_inprocess_dashboard():
            return _users_no_inprocess_dashboard()

        @bp_admin.post("/users_no_inprocess/add")
        @admin_required
        def add_user_no_inprocess() -> ResponseReturnValue:
            return _add_user_no_inprocess()

        @bp_admin.post("/users_no_inprocess/<int:record_id>/delete")
        @admin_required
        def delete_user_no_inprocess(record_id: int) -> ResponseReturnValue:
            return _delete_user_no_inprocess(record_id)

        @bp_admin.post("/users_no_inprocess/<int:record_id>/activate")
        @admin_required
        def activate_user_no_inprocess(record_id: int) -> ResponseReturnValue:
            return _activate_record(record_id)

        @bp_admin.post("/users_no_inprocess/<int:record_id>/deactivate")
        @admin_required
        def deactivate_user_no_inprocess(record_id: int) -> ResponseReturnValue:
            return _deactivate_record(record_id)
