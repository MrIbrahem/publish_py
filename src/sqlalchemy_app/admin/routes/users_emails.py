"""Admin-only routes for managing users not in process."""

from __future__ import annotations

import logging
from typing import List

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue

from ...db_models import ProjectRecord, UserRecord
from ...public.services.project_service import list_projects
from ...public.services.user_service import (
    add_user,
    delete_user,
    get_user,
    get_user_by_username,
    list_users,
    list_users_by_group,
    update_user,
    user_exists,
)
from ...shared.services.page_service import list_of_users_by_translations_count
from ..decorators import admin_required

logger = logging.getLogger(__name__)


def filter_users(users: List[UserRecord], project_name: str):
    if project_name == "All":
        return users

    if project_name == "empty":
        return [x for x in users if not x.user_group]

    users = [x for x in users if x.user_group == project_name]
    return users


def _dashboard():
    """Render the users not in process management dashboard."""

    projects: List[ProjectRecord] = list_projects()

    users: List[UserRecord] = list_users()
    total = len(users)

    project_name = request.args.get("project", "").strip()
    if project_name:
        users = filter_users(users, project_name)

    users_counts: dict[str, int] = list_of_users_by_translations_count()

    users_data = []

    for x in users:
        user_data = x.to_dict()
        user_data["live"] = users_counts.get(x.username) or 0
        users_data.append(user_data)

    # sort data by value
    users_data = sorted(users_data, key=lambda x: x["live"], reverse=True)

    return render_template(
        "admins/users_emails.html",
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
        record = add_user(
            username=username,
            email=email,
            wiki=wiki,
            user_group=user_group,
        )
    except ValueError as exc:
        logger.warning(f"Unable to add user: {exc}")
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
        record = update_user(
            user_id=user_id,
            username=username,
            email=email,
            wiki=wiki,
            user_group=user_group,
        )
    except LookupError as exc:
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
        record = delete_user(record_id)
    except ValueError as exc:
        logger.warning(f"Unable to delete user: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to delete user.")
        flash("Unable to delete user. Please try again.", "danger")
    else:
        flash(f"User '{record.user}' deleted", "success")

    return redirect(url_for("admin.users_emails.dashboard"))


class UsersEmails:
    def __init__(self):
        self.bp = Blueprint("users_emails", __name__, url_prefix="/users_emails")
        self._setup_routes()

    def _setup_routes(self):

        @self.bp.get("/")
        @admin_required
        def dashboard():
            return _dashboard()

        @self.bp.post("/add")
        @admin_required
        def add() -> ResponseReturnValue:
            return _add_user()

        @self.bp.post("/<int:record_id>/delete")
        @admin_required
        def delete(record_id: int) -> ResponseReturnValue:
            return _delete_user(record_id)

        @self.bp.post("/<int:record_id>/update")
        @admin_required
        def update(record_id: int) -> ResponseReturnValue:
            return _update_record(record_id)


users_emails_module = UsersEmails()
