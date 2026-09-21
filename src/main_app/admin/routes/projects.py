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
from flask.views import MethodView

from ...database.services import ProjectService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


class BaseProjectsView(MethodView):
    """Base view for the project management pages.

    Holds the project service shared by every project page and exposes
    the create/update/delete helpers used by the write endpoints. All
    project pages require an administrator.
    """

    decorators = [admin_required]

    def __init__(self) -> None:
        self.project_service = ProjectService()

    def _add_project(self) -> ResponseReturnValue:
        """Create a new project record."""
        g_title = request.form.get("g_title", "").strip()
        if not g_title:
            flash("Title is required.", "danger")
            return redirect(url_for("adminpanel.projects.dashboard"))

        try:
            self.project_service.add_project(
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

        return redirect(url_for("adminpanel.projects.dashboard"))

    def _update_project(self, record_id: int, g_title: str) -> None:
        """Update an existing project record."""

        try:
            record = self.project_service.update_project_title(record_id, g_title)
        except ValueError as exc:
            logger.exception("Unable to update project")
            flash(str(exc), "warning")
        except Exception:
            logger.exception("Unable to update project.")
            flash("Unable to update project. Please try again.", "danger")
        else:
            flash(f"project for '{record.g_title}' updated.", "success")

    def _delete_project(self, record_id: int) -> None:
        """Remove a project record entirely."""

        record = self.project_service.get_record_by_id(record_id)
        if not record:
            logger.error(f"Unable to find project with ID {record_id}")
            flash(f"Unable to find project with ID {record_id}", "warning")
            return

        deleted = self.project_service.delete_record(record)
        if deleted:
            flash(f"project for '{record_id}' removed.", "success")
        else:
            logger.error("Unable to delete project with ID %s", record_id)
            flash(f"Unable to delete project with ID {record_id}", "danger")


class ProjectsDashboardView(BaseProjectsView):
    """Render the projects management dashboard."""

    def get(self) -> str:
        """Render the projects dashboard page."""
        projects = self.project_service.list_projects()

        return render_template(
            "admins/projects.html",
            projects=projects,
        )


class ProjectsAddView(BaseProjectsView):
    """Create a new project record."""

    def post(self) -> ResponseReturnValue:
        """Validate the submitted title and create the project."""
        return self._add_project()


class ProjectsUpdateView(BaseProjectsView):
    """Apply the bulk project edits submitted from the dashboard."""

    def post(self) -> ResponseReturnValue:
        """Delete or rename each submitted project row."""
        projects = request.form.getlist("projects[][g_id]")
        titles = request.form.getlist("projects[][g_title]")
        titles_original = request.form.getlist("titles_original[][g_title]")
        deletes = request.form.getlist("projects[][delete]")

        def get_val(lst: list[str], idx: int) -> str:
            return lst[idx].strip() if idx < len(lst) else ""

        for i, g_id in enumerate(projects):
            record_id = int(g_id)

            g_title = get_val(titles, i)
            g_title_original = get_val(titles_original, i)

            is_deleted = str(record_id) in deletes

            if is_deleted:
                self._delete_project(record_id)
            elif g_title != g_title_original:
                self._update_project(record_id, g_title)

        return redirect(url_for("adminpanel.projects.dashboard"))


class ProjectsDashboard:
    """Registrar wiring the project MethodViews onto a blueprint.

    Endpoint names (``dashboard``, ``add``, ``update``) are preserved from
    the legacy function-based routes so existing
    ``url_for('adminpanel.projects.add')`` calls keep working.
    """

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        """Register the dashboard, add and update endpoints."""
        bp.add_url_rule("/", view_func=ProjectsDashboardView.as_view("dashboard"), methods=["GET"])
        bp.add_url_rule("/add", view_func=ProjectsAddView.as_view("add"), methods=["POST"])
        bp.add_url_rule("/update", view_func=ProjectsUpdateView.as_view("update"), methods=["POST"])


__all__ = [
    "ProjectsDashboard",
]
