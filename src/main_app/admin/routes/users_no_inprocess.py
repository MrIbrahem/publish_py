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
from flask.views import MethodView

from ...database.services import UsersNoInprocessService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


class BaseUsersNoInprocessView(MethodView):
    """Base view for the users-not-in-process management pages.

    Holds the service shared by every users-not-in-process page and
    exposes the activate/deactivate helper used by the toggle endpoints.
    All pages require an administrator.
    """

    decorators = [admin_required]

    def __init__(self) -> None:
        self.service = UsersNoInprocessService()

    def _set_record_active_status(self, record_id: int, is_active: bool) -> ResponseReturnValue:
        """Shared helper to update record active status."""
        action = "activate" if is_active else "deactivate"
        try:
            record = self.service.update_users_no_inprocess(record_id, is_active=is_active)
        except LookupError as exc:
            logger.exception(f"Unable to {action} coordinator.")
            flash(str(exc), "warning")
        except Exception:  # pragma: no cover - defensive guard
            logger.exception(f"Unable to {action} record.")
            flash(f"Unable to {action} record. Please try again.", "danger")
        else:
            state = "activated" if record.is_active else "deactivated"
            flash(f"Record '{record.user}' {state}.", "success")

        return redirect(url_for("adminpanel.users_no_inprocess.dashboard"))


class UsersNoInprocessDashboardView(BaseUsersNoInprocessView):
    """Render the users not in process management dashboard."""

    def get(self) -> str:
        """Render the users table with active/inactive counts."""
        users = self.service.list_users_no_inprocess()
        total = len(users)
        is_active = sum(1 for u in users if u.is_active)

        return render_template(
            "admins/users_no_inprocess.html",
            users=users,
            total_users=total,
            active_users=is_active,
            inactive_users=total - is_active,
        )


class UsersNoInprocessAddView(BaseUsersNoInprocessView):
    """Create a new user not in process record from the submitted username."""

    def post(self) -> ResponseReturnValue:
        """Validate the username and add the user."""

        username = request.form.get("username", "").strip()
        if not username:
            flash("Username is required to add a user.", "danger")
            return redirect(url_for("adminpanel.users_no_inprocess.dashboard"))

        try:
            record = self.service.add_users_no_inprocess(username)
        except ValueError as exc:
            logger.exception("Unable to add user")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to add user.")
            flash("Unable to add user. Please try again.", "danger")
        else:
            flash(f"User '{record.user}' added to 'not in process' list.", "success")

        return redirect(url_for("adminpanel.users_no_inprocess.dashboard"))


class UsersNoInprocessDeleteView(BaseUsersNoInprocessView):
    """Remove a user not in process record entirely."""

    def post(self, record_id: int) -> ResponseReturnValue:
        """Delete the user identified by ``record_id``."""

        try:
            record = self.service.delete(record_id)
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

        return redirect(url_for("adminpanel.users_no_inprocess.dashboard"))


class UsersNoInprocessActivateView(BaseUsersNoInprocessView):
    """Activate a user not in process record."""

    def post(self, record_id: int) -> ResponseReturnValue:
        """Mark the record identified by ``record_id`` as active."""
        return self._set_record_active_status(record_id, True)


class UsersNoInprocessDeactivateView(BaseUsersNoInprocessView):
    """Deactivate a user not in process record."""

    def post(self, record_id: int) -> ResponseReturnValue:
        """Mark the record identified by ``record_id`` as inactive."""
        return self._set_record_active_status(record_id, False)


class UsersNoInprocess:
    """Registrar wiring the users-not-in-process MethodViews onto a blueprint.

    Endpoint names (``dashboard``, ``add``, ``delete``, ``activate``,
    ``deactivate``) are preserved from the legacy function-based routes
    so existing ``url_for('adminpanel.users_no_inprocess.add')`` calls
    keep working.
    """

    def register(self, bp: Blueprint) -> None:
        """Register the dashboard and the user write endpoints."""
        bp.add_url_rule("/", view_func=UsersNoInprocessDashboardView.as_view("dashboard"), methods=["GET"])
        bp.add_url_rule("/add", view_func=UsersNoInprocessAddView.as_view("add"), methods=["POST"])
        bp.add_url_rule(
            "/<int:record_id>/delete", view_func=UsersNoInprocessDeleteView.as_view("delete"), methods=["POST"]
        )
        bp.add_url_rule(
            "/<int:record_id>/activate",
            view_func=UsersNoInprocessActivateView.as_view("activate"),
            methods=["POST"],
        )
        bp.add_url_rule(
            "/<int:record_id>/deactivate",
            view_func=UsersNoInprocessDeactivateView.as_view("deactivate"),
            methods=["POST"],
        )


__all__ = [
    "UsersNoInprocess",
]
