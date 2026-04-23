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

from ...shared.services.project_service import (
    add_project,
    delete_project,
    list_projects,
    update_project_title,
)
from ..decorators import admin_required

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
    g_title = request.form.get("g_title", "").strip()
    if not g_title:
        flash("Title is required.", "danger")
        return redirect(url_for("admin.projects.dashboard"))

    try:
        add_project(
            g_title=g_title,
        )
    except ValueError as exc:
        logger.warning(f"Unable to add project: {exc}")
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
        record = update_project_title(record_id, g_title)
    except ValueError as exc:
        logger.warning(f"Unable to update project: {exc}")
        flash(str(exc), "warning")
    except Exception:
        logger.exception("Unable to update project.")
        flash("Unable to update project. Please try again.", "danger")
    else:
        flash(f"project for '{record.g_title}' updated.", "success")


def _delete_project(record_id: int) -> None:
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


class ProjectsDashboard:
    def __init__(self):
        self.bp = Blueprint("projects", __name__, url_prefix="/projects")
        self._setup_routes()

    def _setup_routes(self):
        @self.bp.get("/")
        @admin_required
        def dashboard():
            return _projects_dashboard()

        @self.bp.post("/add")
        @admin_required
        def add() -> ResponseReturnValue:
            return _add_project()

        @self.bp.post("/update")
        @admin_required
        def update() -> ResponseReturnValue:
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


projects_module = ProjectsDashboard()
