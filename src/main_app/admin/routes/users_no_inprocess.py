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

from ...db.services.users import (
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
    is_active = sum(1 for u in users if u.is_active)

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
        return redirect(url_for("admin.users_no_inprocess.dashboard"))

    try:
        record = add_users_no_inprocess(username)
    except ValueError as exc:
        logger.exception("Unable to add user")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to add user.")
        flash("Unable to add user. Please try again.", "danger")
    else:
        flash(f"User '{record.user}' added to 'not in process' list.", "success")

    return redirect(url_for("admin.users_no_inprocess.dashboard"))


def _set_record_active_status(record_id: int, is_active: bool) -> ResponseReturnValue:
    """Shared helper to update record active status."""
    action = "activate" if is_active else "deactivate"
    try:
        record = update_users_no_inprocess(record_id, is_active=is_active)
    except LookupError as exc:
        logger.exception(f"Unable to {action} coordinator.")
        flash(str(exc), "warning")
    except Exception:  # pragma: no cover - defensive guard
        logger.exception(f"Unable to {action} record.")
        flash(f"Unable to {action} record. Please try again.", "danger")
    else:
        state = "activated" if record.is_active else "deactivated"
        flash(f"Record '{record.user}' {state}.", "success")

    return redirect(url_for("admin.users_no_inprocess.dashboard"))


def _delete_user_no_inprocess(record_id: int) -> ResponseReturnValue:
    """Remove a user not in process record entirely."""

    try:
        record = delete_users_no_inprocess(record_id)
        if not record:
            raise ValueError(f"Unable to delete user with ID {record_id}")
    except ValueError as exc:
        logger.exception("Unable to delete user")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to delete user.")
        flash("Unable to delete user. Please try again.", "danger")
    else:
        flash(f"User '{record_id}' removed from 'not in process' list.", "success")

    return redirect(url_for("admin.users_no_inprocess.dashboard"))


class UsersNoInprocess:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(admin_required(self.dashboard))
        self.bp.post("/add")(admin_required(self.add))
        self.bp.post("/<int:record_id>/delete")(admin_required(self.delete))
        self.bp.post("/<int:record_id>/activate")(admin_required(self.activate))
        self.bp.post("/<int:record_id>/deactivate")(admin_required(self.deactivate))

    def dashboard(self):
        return _users_no_inprocess_dashboard()

    def add(self) -> ResponseReturnValue:
        return _add_user_no_inprocess()

    def delete(self, record_id: int) -> ResponseReturnValue:
        return _delete_user_no_inprocess(record_id)

    def activate(self, record_id: int) -> ResponseReturnValue:
        return _set_record_active_status(record_id, True)

    def deactivate(self, record_id: int) -> ResponseReturnValue:
        return _set_record_active_status(record_id, False)


__all__ = [
    "UsersNoInprocess",
]
