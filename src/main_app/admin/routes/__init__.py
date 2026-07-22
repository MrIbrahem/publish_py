"""Admin blueprint package."""

from .add_translate import add_bp
from .campaigns import campaigns_module
from .coordinators import CoordinatorsRoutes
from .email_msg import bp_msg
from .full_translators import fulltranslators_module
from .language_settings import languagesettings_module
from .pages_users_to_main import pages_users_to_main_bp
from .projects import projects_module
from .qids.qids import qids_module
from .qids.qids_others import qids_others_module
from .settings import settings_module
from .stat import stat_bp
from .translated import translated_bp
from .translated_users import translated_users_bp
from .tt import tt_bp
from .users_emails import users_emails_module
from .users_no_inprocess import usersnoinprocess_module

__all__ = [
    "CoordinatorsRoutes",
    "add_bp",
    "campaigns_module",
    "bp_msg",
    "fulltranslators_module",
    "languagesettings_module",
    "pages_users_to_main_bp",
    "projects_module",
    "qids_module",
    "qids_others_module",
    "settings_module",
    "stat_bp",
    "translated_bp",
    "translated_users_bp",
    "tt_bp",
    "users_emails_module",
    "usersnoinprocess_module",
]
