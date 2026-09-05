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

from ...database.services import ProjectService
from ..decorators import admin_required

logger = logging.getLogger(__name__)


class ProjectsDashboard:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self.project_service = ProjectService()
        self._setup_routes()

    def _setup_routes(self) -> None:

        routes = [
            ("/", "GET", self.dashboard),
            ("/add", "POST", self.add),
            ("/update", "POST", self.update),
        ]
        for rule, method, target in routes:
            self.bp.route(rule, methods=[method])(admin_required(target))

    def dashboard(self):
        return self._projects_dashboard()

    def add(self) -> ResponseReturnValue:
        return self._add_project()

    def update(self) -> ResponseReturnValue:
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

    def _projects_dashboard(self):
        """Render the projects management dashboard."""

        projects = self.project_service.list_projects()

        return render_template(
            "admins/projects.html",
            projects=projects,
        )

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


__all__ = [
    "ProjectsDashboard",
]
