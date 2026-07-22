"""Admin blueprint package."""

from .add_translate import AddTranslateRoutes
from .campaigns import CampaignsDashboard
from .coordinators import CoordinatorsRoutes
from .email_msg import EmailMsgRoutes
from .full_translators import FullTranslators
from .language_settings import LanguageSettings
from .pages_users_to_main import PagesUsersMainRoutes
from .projects import ProjectsDashboard
from .qids.qids import QidsRoutes
from .qids.qids_others import QidsOthersRoutes
from .settings import SettingsRoutes
from .stat import StaticsRoutes
from .translated import TranslatedRoutes
from .translated_users import TranslatedUsersRoutes
from .tt import TranslateTypeRoutes
from .users_emails import UsersEmails
from .users_no_inprocess import UsersNoInprocess

__all__ = [
    "CoordinatorsRoutes",
    "AddTranslateRoutes",
    "EmailMsgRoutes",
    "PagesUsersMainRoutes",
    "ProjectsDashboard",
    "QidsRoutes",
    "QidsOthersRoutes",
    "StaticsRoutes",
    "TranslatedRoutes",
    "TranslatedUsersRoutes",
    "TranslateTypeRoutes",
    "UsersEmails",
    "UsersNoInprocess",
    "SettingsRoutes",
    "CampaignsDashboard",
    "FullTranslators",
    "LanguageSettings",
]
