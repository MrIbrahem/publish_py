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

from ..sqlalchemy_db.services.users_no_inprocess_service import (
    add_users_no_inprocess,
    delete_users_no_inprocess,
    list_users_no_inprocess,
    update_users_no_inprocess,
)
from ..decorators import admin_required

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


def _update_user_no_inprocess_active(record_id: int) -> ResponseReturnValue:
    """Toggle the active flag for a user not in process record."""

    active = 1 if request.form.get("active") == "1" else 0
    try:
        record = update_users_no_inprocess(record_id, active=active)
    except ValueError as exc:
        logger.warning(f"Unable to update user: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to update user.")
        flash("Unable to update user status. Please try again.", "danger")
    else:
        state = "activated" if record.active else "deactivated"
        flash(f"User '{record.user}' {state}.", "success")

    return redirect(url_for("admin.users_no_inprocess_dashboard"))


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

        @bp_admin.post("/users_no_inprocess/<int:record_id>/active")
        @admin_required
        def update_user_no_inprocess_active(record_id: int) -> ResponseReturnValue:
            return _update_user_no_inprocess_active(record_id)

        @bp_admin.post("/users_no_inprocess/<int:record_id>/delete")
        @admin_required
        def delete_user_no_inprocess(record_id: int) -> ResponseReturnValue:
            return _delete_user_no_inprocess(record_id)
