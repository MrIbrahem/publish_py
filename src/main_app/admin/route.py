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

from .decorators import admin_required
from .routes.add_translate import add_bp
from .routes.campaigns import campaigns_module
from .routes.categories import categories_dashboard
from .routes.coordinators import coordinators_module
from .routes.email_msg import bp_msg
from .routes.full_translators import fulltranslators_module
from .routes.language_settings import languagesettings_module
from .routes.last import last_translations_dashboard
from .routes.pages_users_to_main import pages_users_to_main_bp
from .routes.projects import projects_module
from .routes.qids.qids import qids_module
from .routes.qids.qids_others import qids_others_module
from .routes.settings import settings_module
from .routes.stat import stat_bp
from .routes.translated import translated_bp
from .routes.translated_users import translated_users_bp
from .routes.tt import tt_bp
from .routes.users_emails import users_emails_module
from .routes.users_no_inprocess import usersnoinprocess_module
from .sidebar import create_side

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


@bp_admin.get("/edit_done")
@admin_required
def edit_done() -> str:
    return render_template("admins/close_btn.html")


@bp_admin.get("/categories")
@admin_required
def categories_dashboard_route():
    return categories_dashboard()


def register_blueprints(bp_admin: Blueprint) -> None:
    bp_admin.register_blueprint(coordinators_module.bp)
    bp_admin.register_blueprint(fulltranslators_module.bp)
    bp_admin.register_blueprint(usersnoinprocess_module.bp)
    bp_admin.register_blueprint(languagesettings_module.bp)
    bp_admin.register_blueprint(add_bp)
    bp_admin.register_blueprint(tt_bp)
    bp_admin.register_blueprint(translated_bp)
    bp_admin.register_blueprint(translated_users_bp)

    bp_admin.register_blueprint(bp_msg)
    bp_admin.register_blueprint(qids_module.bp)
    bp_admin.register_blueprint(qids_others_module.bp)
    bp_admin.register_blueprint(pages_users_to_main_bp)
    bp_admin.register_blueprint(stat_bp)
    # Templates(bp_admin)
    bp_admin.register_blueprint(settings_module.bp)
    bp_admin.register_blueprint(projects_module.bp)
    bp_admin.register_blueprint(campaigns_module.bp)
    # Jobs(bp_admin)
    # OwidCharts(bp_admin)
    bp_admin.register_blueprint(users_emails_module.bp)


register_blueprints(bp_admin)


__all__ = [
    "bp_admin",
    "register_blueprints",
]
