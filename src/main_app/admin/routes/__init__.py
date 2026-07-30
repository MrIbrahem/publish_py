"""Admin blueprint package."""

from dataclasses import dataclass, field
from typing import Any

from .add_translate import AddTranslateRoutes
from .campaigns import CampaignsDashboard
from .coordinators import CoordinatorsRoutes
from .email_msg import EmailMsgRoutes
from .errors_route import CheckErrorsRoutes
from .full_translators import FullTranslators
from .language_settings import LanguageSettings
from .pages_users_to_main import PagesUsersMainRoutes
from .projects import ProjectsDashboard
from .qids.qids import QidsRoutes
from .qids.qids_others import QidsOthersRoutes
from .settings import SettingsRoutes
from .stat import StaticsRoutes
from .translated.translated_main import TranslatedRoutes
from .translated.translated_users import TranslatedUsersRoutes
from .tt import TranslateTypeRoutes
from .users_emails import UsersEmails
from .users_no_inprocess import UsersNoInprocess


@dataclass(frozen=True)
class AdminRouteModule:
    route_cls: type
    name: str
    url_prefix: str = ""
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


ADMIN_ROUTE_MODULES: list[AdminRouteModule] = [
    AdminRouteModule(CoordinatorsRoutes, "coordinators", "/coordinators"),
    AdminRouteModule(TranslateTypeRoutes, "tt", "/tt"),
    AdminRouteModule(TranslatedRoutes, "translated", "/translated"),
    AdminRouteModule(TranslatedUsersRoutes, "translated_users", "/translated_users"),
    AdminRouteModule(StaticsRoutes, "stat", "/stat"),
    AdminRouteModule(PagesUsersMainRoutes, "pages_users_to_main", "/pages_users_to_main"),
    AdminRouteModule(EmailMsgRoutes, "email_msg", "/email_msg"),
    AdminRouteModule(AddTranslateRoutes, "add", "/add"),
    AdminRouteModule(ProjectsDashboard, "projects", "/projects"),
    AdminRouteModule(CampaignsDashboard, "campaigns", "/campaigns"),
    AdminRouteModule(FullTranslators, "full_translators", "/full_translators"),
    AdminRouteModule(LanguageSettings, "language_settings", "/language_settings"),
    AdminRouteModule(SettingsRoutes, "settings", "/settings"),
    AdminRouteModule(UsersEmails, "users_emails", "/users_emails"),
    AdminRouteModule(UsersNoInprocess, "users_no_inprocess", "/users_no_inprocess"),
    AdminRouteModule(QidsRoutes, "qids", "/qids"),
    AdminRouteModule(QidsOthersRoutes, "qids_others", "/qids_others"),
    AdminRouteModule(route_cls=CheckErrorsRoutes, name="errors", url_prefix="/errors"),
]

__all__ = [
    "ADMIN_ROUTE_MODULES",
]
