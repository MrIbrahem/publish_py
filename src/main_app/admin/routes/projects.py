"""
Admin-only routes for managing projects.
"""

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

from ...db.services.content import ProjectService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


def _projects_dashboard():
    """Render the projects management dashboard."""

    project_service = ProjectService()
    projects = project_service.list_projects()

    return render_template(
        "admins/projects.html",
        projects=projects,
    )


def _add_project() -> ResponseReturnValue:
    """Create a new project record."""
    g_title = request.form.get("g_title", "").strip()
    if not g_title:
        flash("Title is required.", "danger")
        return redirect(url_for("admin.projects.dashboard"))

    try:
        project_service = ProjectService()
        project_service.add_project(
            g_title=g_title,
        )
    except ValueError as exc:
        logger.exception("Unable to add project")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to add project.")
        flash("Unable to add project. Please try again.", "danger")
    else:
        flash(f"project for '{g_title}' added.", "success")

    return redirect(url_for("admin.projects.dashboard"))


def _update_project(record_id: int, g_title: str) -> None:
    """Update an existing project record."""

    try:
        project_service = ProjectService()
        record = project_service.update_project_title(record_id, g_title)
    except ValueError as exc:
        logger.exception("Unable to update project")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to update project.")
        flash("Unable to update project. Please try again.", "danger")
    else:
        flash(f"project for '{record.g_title}' updated.", "success")


def _delete_project(record_id: int) -> None:
    """Remove a project record entirely."""

    project_service = ProjectService()
    record = project_service.get_record_by_id(record_id)
    if not record:
        logger.error(f"Unable to find project with ID {record_id}")
        flash(f"Unable to find project with ID {record_id}", "warning")
        return

    deleted = project_service.delete_record(record)
    if deleted:
        flash(f"project for '{record_id}' removed.", "success")
    else:
        logger.exception(f"Unable to delete project with ID {record_id}")


class ProjectsDashboard:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(admin_required(self.dashboard))
        self.bp.post("/add")(admin_required(self.add))
        self.bp.post("/update")(admin_required(self.update))

    def dashboard(self):
        return _projects_dashboard()

    def add(self) -> ResponseReturnValue:
        return _add_project()

    def update(self) -> ResponseReturnValue:
        projects = request.form.getlist("projects[][g_id]")
        titles = request.form.getlist("projects[][g_title]")
        titles_original = request.form.getlist("titles_original[][g_title]")
        deletes = request.form.getlist("projects[][delete]")

        for i, g_id in enumerate(projects):
            record_id = int(g_id)
            g_title = titles[i] if i < len(titles) else ""
            g_title_original = titles_original[i] if i < len(titles_original) else ""
            is_deleted = str(record_id) in deletes

            if is_deleted:
                _delete_project(record_id)
            elif g_title != g_title_original:
                _update_project(record_id, g_title)

        return redirect(url_for("admin.projects.dashboard"))


__all__ = [
    "ProjectsDashboard",
]
