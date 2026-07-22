"""Admin blueprint package."""

from flask import Blueprint, Flask

from .admin_panel import AdminPanel
from .routes import (
    CoordinatorsRoutes,
    add_bp,
    bp_msg,
    campaigns_module,
    fulltranslators_module,
    languagesettings_module,
    pages_users_to_main_bp,
    projects_module,
    qids_module,
    qids_others_module,
    settings_module,
    stat_bp,
    translated_bp,
    translated_users_bp,
    tt_bp,
    users_emails_module,
    usersnoinprocess_module,
)


def register_bp_admin_blueprints(app: Flask) -> None:
    bp_admin = Blueprint("admin", __name__, url_prefix="/admin")
    admin_model = AdminPanel(bp_admin)

    coordinators_bp = Blueprint("coordinators", __name__, url_prefix="/coordinators")
    coordinators_module = CoordinatorsRoutes(coordinators_bp)

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
    bp_admin.register_blueprint(settings_module.bp)
    bp_admin.register_blueprint(projects_module.bp)
    bp_admin.register_blueprint(campaigns_module.bp)
    bp_admin.register_blueprint(users_emails_module.bp)

    app.register_blueprint(bp_admin)


__all__ = [
    "register_bp_admin_blueprints",
]
