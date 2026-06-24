"""
Admin Blueprints
"""

from flask import Blueprint

from .admin_panel import admin_route_module
from .routes.add_translate import add_bp
from .routes.campaigns import campaigns_module
from .routes.coordinators import coordinators_module
from .routes.email_msg import bp_msg
from .routes.full_translators import fulltranslators_module
from .routes.language_settings import languagesettings_module
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


def register_bp_admin_blueprints(_bp: Blueprint) -> None:
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
    # Templates(bp_admin)
    _bp.register_blueprint(settings_module.bp)
    _bp.register_blueprint(projects_module.bp)
    _bp.register_blueprint(campaigns_module.bp)
    # Jobs(bp_admin)
    # OwidCharts(bp_admin)
    _bp.register_blueprint(users_emails_module.bp)


register_bp_admin_blueprints(admin_route_module.bp)
