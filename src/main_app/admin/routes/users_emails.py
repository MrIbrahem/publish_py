"""Admin-only routes for managing user emails and groups."""

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

from ...database.models import ProjectRecord, UserRecord
from ...database.services import LeaderboardService, ProjectService, UsersService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


def filter_users(users: list[UserRecord], project_name: str) -> list[UserRecord]:
    if project_name == "All":
        return users

    if project_name == "empty":
        return [x for x in users if not x.user_group]

    users = [x for x in users if x.user_group == project_name]
    return users


class BaseUsersEmailsView(MethodView):
    """Base view for the user-emails management pages.

    Holds the services shared by every user-emails page. All user-emails
    pages require an administrator.
    """

    decorators = [admin_required]

    def __init__(self) -> None:
        self.leaderboard_service = LeaderboardService()
        self.projects_service = ProjectService()
        self.user_service = UsersService()


class UsersEmailsDashboardView(BaseUsersEmailsView):
    """Render the users not in process management dashboard."""

    def get(self) -> str:
        """Render the users table filtered by the selected project."""
        users: list[UserRecord] = self.user_service.list_users()

        projects: list[ProjectRecord] = self.projects_service.list_projects()

        users_counts: dict[str, int] = self.leaderboard_service.list_of_users_by_translations_count()

        total = len(users)

        project_name = request.args.get("project", "").strip()
        if project_name:
            users = filter_users(users, project_name)

        users_data = []

        for x in users:
            user_data = x.to_json()
            user_data["live"] = users_counts.get(x.username) or 0
            users_data.append(user_data)

        # sort data by value
        users_data = sorted(users_data, key=lambda x: x["live"], reverse=True)

        return render_template(
            "admins/users_emails/index.html",
            users=users_data,
            projects=projects,
            project_selected=project_name,
            total_users=total,
        )


class UsersEmailsEditView(BaseUsersEmailsView):
    """Render the edit popup for a single user."""

    def get(self, record_id: int) -> ResponseReturnValue:
        """Render the edit form for the user identified by ``record_id``."""
        user = self.user_service.get_user(record_id)
        if not user:
            flash(f"User with ID {record_id} not found.", "danger")
            return redirect(url_for("adminpanel.users_emails.dashboard"))
        return render_template("admins/users_emails/edit.html", row=user)


class UsersEmailsAddView(BaseUsersEmailsView):
    """Create a new user not in process record from the submitted username."""

    def post(self) -> ResponseReturnValue:
        """Create a new user not in process record from the submitted username."""

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        wiki = request.form.get("wiki", "").strip()
        user_group = request.form.get("user_group", "").strip()

        if not username:
            flash("Username is required to add a user.", "danger")
            return redirect(url_for("adminpanel.users_emails.dashboard"))

        try:
            record = self.user_service.create_user(
                username=username,
                email=email,
                wiki=wiki,
                user_group=user_group,
            )
        except ValueError as exc:
            logger.exception("Unable to add user")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to add user.")
            flash("Unable to add user. Please try again.", "danger")
        else:
            flash(f"User '{record.username}' added to 'not in process' list.", "success")

        return redirect(url_for("adminpanel.users_emails.dashboard"))


class UsersEmailsUpdateView(BaseUsersEmailsView):
    """Update an existing user record."""

    def post(self, record_id: int) -> ResponseReturnValue:
        """update user data"""
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        wiki = request.form.get("wiki", "").strip()
        user_group = request.form.get("user_group", "").strip()

        if not username:
            flash("Username is required to add a user.", "danger")
            return redirect(url_for("adminpanel.users_emails.dashboard"))

        try:
            record = self.user_service.update_user(
                user_id=record_id,
                username=username,
                email=email,
                wiki=wiki,
                user_group=user_group,
            )
        except ValueError as exc:
            logger.exception("Unable to update User.")
            flash(str(exc), "warning")
        except Exception:  # pragma: no cover - defensive guard
            logger.exception("Unable to update User.")
            flash("Unable to update User. Please try again.", "danger")
        else:
            flash(f"User '{record.username}' updated", "success")

        return redirect(url_for("adminpanel.users_emails.dashboard"))


class UsersEmailsDeleteView(BaseUsersEmailsView):
    """Remove a user not in process record entirely."""

    def post(self, record_id: int) -> ResponseReturnValue:
        """Delete the user identified by ``record_id``."""

        try:
            record = self.user_service.delete(record_id)
            if not record:
                raise ValueError(f"Unable to delete user with ID {record_id}")
        except ValueError as exc:
            logger.exception("Unable to delete user")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to delete user.")
            flash("Unable to delete user. Please try again.", "danger")
        else:
            flash(f"User '{record_id}' deleted", "success")

        return redirect(url_for("adminpanel.users_emails.dashboard"))


class UsersEmails:
    """Registrar wiring the user-emails MethodViews onto a blueprint.

    Endpoint names (``dashboard``, ``add``, ``delete``, ``update``,
    ``edit``) are preserved from the legacy function-based routes so
    existing ``url_for('adminpanel.users_emails.edit')`` calls keep
    working.
    """

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the dashboard and the user write endpoints."""
        bp.add_url_rule("/", view_func=UsersEmailsDashboardView.as_view("dashboard"), methods=["GET"])
        bp.add_url_rule("/add", view_func=UsersEmailsAddView.as_view("add"), methods=["POST"])
        bp.add_url_rule("/<int:record_id>/delete", view_func=UsersEmailsDeleteView.as_view("delete"), methods=["POST"])
        bp.add_url_rule("/<int:record_id>/update", view_func=UsersEmailsUpdateView.as_view("update"), methods=["POST"])
        bp.add_url_rule("/<int:record_id>/edit", view_func=UsersEmailsEditView.as_view("edit"), methods=["GET"])


__all__ = [
    "UsersEmails",
]
