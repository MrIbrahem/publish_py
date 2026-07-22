"""
Admin Blueprints
"""

from flask import Blueprint

from .admin_panel import AdminPanelRoutes
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


def register_bp_admin_blueprints() -> None:

    _bp = Blueprint("admin", __name__, url_prefix="/admin")
    admin_route_module = AdminPanelRoutes(_bp)

    coordinators_bp = Blueprint("coordinators", __name__, url_prefix="/coordinators")
    coordinators_module = CoordinatorsRoutes(coordinators_bp)

    _bp.register_blueprint(coordinators_module.bp)
    _bp.register_blueprint(fulltranslators_module.bp)
    _bp.register_blueprint(usersnoinprocess_module.bp)
    _bp.register_blueprint(languagesettings_module.bp)
    _bp.register_blueprint(add_bp)
    _bp.register_blueprint(tt_bp)
    _bp.register_blueprint(translated_bp)
    _bp.register_blueprint(translated_users_bp)

    _bp.register_blueprint(bp_msg)
    _bp.register_blueprint(qids_module.bp)
    _bp.register_blueprint(qids_others_module.bp)
    _bp.register_blueprint(pages_users_to_main_bp)
    _bp.register_blueprint(stat_bp)
    _bp.register_blueprint(settings_module.bp)
    _bp.register_blueprint(projects_module.bp)
    _bp.register_blueprint(campaigns_module.bp)
    _bp.register_blueprint(users_emails_module.bp)


register_bp_admin_blueprints()
