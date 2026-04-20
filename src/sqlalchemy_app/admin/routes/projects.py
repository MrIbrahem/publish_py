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

from ..decorators import admin_required
from ...public.services.project_service import (
    list_projects,
    add_project,
    update_project_title,
    delete_project,
)

logger = logging.getLogger(__name__)


def _projects_dashboard():
    """Render the projects management dashboard."""

    projects = list_projects()

    return render_template(
        "admins/projects.html",
        projects=projects,
    )


def _add_project() -> ResponseReturnValue:
    """Create a new project record."""
    ...


def _update_project(record_id: int) -> ResponseReturnValue:
    """Update an existing project record."""

    g_title = request.form.get("g_title")

    try:
        record = update_project_title(record_id, g_title)
    except ValueError as exc:
        logger.warning(f"Unable to update project: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to update project.")
        flash("Unable to update project. Please try again.", "danger")
    else:
        flash(f"project for '{record.g_title}' updated.", "success")

    return redirect(url_for("admin.projects_dashboard"))


def _delete_project(record_id: int) -> ResponseReturnValue:
    """Remove a project record entirely."""

    try:
        record = delete_project(record_id)
    except ValueError as exc:
        logger.warning(f"Unable to delete project: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to delete project.")
        flash("Unable to delete project. Please try again.", "danger")
    else:
        flash(f"project for '{record.g_title}' removed.", "success")

    return redirect(url_for("admin.projects_dashboard"))


class ProjectsDashboard:
    def __init__(self, bp_admin: Blueprint):
        @bp_admin.get("/projects")
        @admin_required
        def projects_dashboard():
            return _projects_dashboard()

        @bp_admin.post("/projects/add")
        @admin_required
        def add_project_record() -> ResponseReturnValue:
            return _add_project()

        @bp_admin.post("/projects/<int:record_id>/update")
        @admin_required
        def update_project_route(record_id: int) -> ResponseReturnValue:
            return _update_project(record_id)

        @bp_admin.post("/projects/<int:record_id>/delete")
        @admin_required
        def delete_project_route(record_id: int) -> ResponseReturnValue:
            return _delete_project(record_id)
