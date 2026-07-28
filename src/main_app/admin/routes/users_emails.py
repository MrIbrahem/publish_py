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

from ...db.models import ProjectRecord, UserRecord
from ...db.services import ProjectService
from ...db.services import LeaderboardService
from ...db.services import UsersService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


def filter_users(users: list[UserRecord], project_name: str):
    if project_name == "All":
        return users

    if project_name == "empty":
        return [x for x in users if not x.user_group]

    users = [x for x in users if x.user_group == project_name]
    return users


def _dashboard(users: list[UserRecord], users_counts: dict[str, int], projects: list[ProjectRecord],):
    """Render the users not in process management dashboard."""

    total = len(users)

    project_name = request.args.get("project", "").strip()
    if project_name:
        users = filter_users(users, project_name)

    users_data = []

    for x in users:
        user_data = x.to_dict()
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


def _add_user() -> ResponseReturnValue:
    """Create a new user not in process record from the submitted username."""

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    wiki = request.form.get("wiki", "").strip()
    user_group = request.form.get("user_group", "").strip()

    if not username:
        flash("Username is required to add a user.", "danger")
        return redirect(url_for("admin.users_emails.dashboard"))

    try:
        service = UsersService()
        record = service.create_user(
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

    return redirect(url_for("admin.users_emails.dashboard"))


def _update_record(user_id: int) -> ResponseReturnValue:
    """update user data"""
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    wiki = request.form.get("wiki", "").strip()
    user_group = request.form.get("user_group", "").strip()

    if not username:
        flash("Username is required to add a user.", "danger")
        return redirect(url_for("admin.users_emails.dashboard"))

    try:
        service = UsersService()
        record = service.update_user(
            user_id=user_id,
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

    return redirect(url_for("admin.users_emails.dashboard"))


def _delete_user(record_id: int) -> ResponseReturnValue:
    """Remove a user not in process record entirely."""

    try:
        service = UsersService()
        record = service.delete(record_id)
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

    return redirect(url_for("admin.users_emails.dashboard"))


class UsersEmails:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.user_service = UsersService()
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(admin_required(self.dashboard))
        self.bp.post("/add")(admin_required(self.add))
        self.bp.post("/<int:record_id>/delete")(admin_required(self.delete))
        self.bp.post("/<int:record_id>/update")(admin_required(self.update))
        self.bp.route("/<int:record_id>/edit", methods=["GET"])(admin_required(self.edit))

    def dashboard(self):
        users: list[UserRecord] = self.user_service.list_users()

        projects_service = ProjectService()
        projects: list[ProjectRecord] = projects_service.list_projects()

        lederboard_service = LeaderboardService()
        users_counts: dict[str, int] = lederboard_service.list_of_users_by_translations_count()

        return _dashboard(users, users_counts, projects)

    def add(self) -> ResponseReturnValue:
        return _add_user()

    def delete(self, record_id: int) -> ResponseReturnValue:
        return _delete_user(record_id)

    def update(self, record_id: int) -> ResponseReturnValue:
        return _update_record(record_id)

    def edit(self, record_id: int) -> ResponseReturnValue:
        user = self.user_service.get_user(record_id)
        if not user:
            flash(f"User with ID {record_id} not found.", "danger")
            return redirect(url_for("admin.users_emails.dashboard"))
        return render_template("admins/users_emails/edit.html", row=user)


__all__ = [
    "UsersEmails",
]
