"""Admin-only routes for managing coordinator access."""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)

# from ..admin_routes import (
#     Coordinators,
#     Jobs,
#     OwidCharts,
#     Templates,
# )
from ..decorators import admin_required
from ..sidebar import create_side
from .campaigns import campaigns_module
from .coordinators import Coordinators
from .full_translators import FullTranslators
from .language_settings import LanguageSettings
from .last import last_translations_dashboard
from .projects import ProjectsDashboard
from .settings import SettingsRoutes
from .users_emails import users_emails_module
from .users_no_inprocess import UsersNoInprocess

logger = logging.getLogger(__name__)

bp_admin = Blueprint("admin", __name__, url_prefix="/admin")


@bp_admin.app_context_processor
def inject_sidebar():
    path_parts = request.path.strip("/").split("/")
    active_route = path_parts[1] if len(path_parts) > 1 else ""
    # logger.debug(f"Injecting sidebar for path='{request.path}'")
    sidebar_html = create_side(active_route=active_route)
    return {"sidebar": sidebar_html}


@bp_admin.get("/")
@admin_required
def index():
    return redirect(url_for("admin.last_dashboard"))


@bp_admin.get("/last")
@admin_required
def last_dashboard():
    return last_translations_dashboard()


@bp_admin.get("/reports")
@admin_required
def reports():
    return render_template("admins/reports.html")


@bp_admin.get("/process")
@admin_required
def in_process_dashboard():
    return render_template("admins/in_process.html")


@bp_admin.get("/process_total")
@admin_required
def in_process_total_dashboard():
    """Render the in-process totals dashboard."""
    return render_template(
        "admins/in_process_total.html",
    )


def register_blueprints(bp_admin: Blueprint) -> None:
    Coordinators(bp_admin)
    FullTranslators(bp_admin)
    UsersNoInprocess(bp_admin)
    LanguageSettings(bp_admin)
    # Templates(bp_admin)
    SettingsRoutes(bp_admin)
    ProjectsDashboard(bp_admin)
    bp_admin.register_blueprint(campaigns_module.bp)
    # Jobs(bp_admin)
    # OwidCharts(bp_admin)
    bp_admin.register_blueprint(users_emails_module.bp)


register_blueprints(bp_admin)
