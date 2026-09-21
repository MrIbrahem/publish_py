"""Admin blueprint package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from flask import Blueprint

from .add_translate import AddTranslateView
from .campaigns import CampaignsDashboard
from .coordinators import CoordinatorView
from .errors_route import CheckErrorsView
from .full_translators import FullTranslators
from .language_settings import LanguageSettings
from .msg import EmailMsgView
from .pages_users_to_main import PagesUsersMainRoutes
from .projects import ProjectsDashboard
from .qids.qids import QidsView
from .qids.qids_others import QidsOthersView
from .settings import SettingsRoutes
from .stat import StaticsRoutes
from .translated.translated_main import TranslatedView
from .translated.translated_users import TranslatedUsersView
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
    AdminRouteModule(route_cls=CoordinatorView, name="coordinators", url_prefix="/coordinators"),
    AdminRouteModule(route_cls=TranslateTypeRoutes, name="tt", url_prefix="/tt"),
    AdminRouteModule(route_cls=TranslatedView, name="translated", url_prefix="/translated"),
    AdminRouteModule(route_cls=TranslatedUsersView, name="translated_users", url_prefix="/translated_users"),
    AdminRouteModule(route_cls=StaticsRoutes, name="stat", url_prefix="/stat"),
    AdminRouteModule(route_cls=PagesUsersMainRoutes, name="pages_users_to_main", url_prefix="/pages_users_to_main"),
    AdminRouteModule(route_cls=EmailMsgView, name="email_msg", url_prefix="/email_msg"),
    AdminRouteModule(route_cls=AddTranslateView, name="add", url_prefix="/add"),
    AdminRouteModule(route_cls=ProjectsDashboard, name="projects", url_prefix="/projects"),
    AdminRouteModule(route_cls=CampaignsDashboard, name="campaigns", url_prefix="/campaigns"),
    AdminRouteModule(route_cls=FullTranslators, name="full_translators", url_prefix="/full_translators"),
    AdminRouteModule(route_cls=LanguageSettings, name="language_settings", url_prefix="/language_settings"),
    AdminRouteModule(route_cls=SettingsRoutes, name="settings", url_prefix="/settings"),
    AdminRouteModule(route_cls=UsersEmails, name="users_emails", url_prefix="/users_emails"),
    AdminRouteModule(route_cls=UsersNoInprocess, name="users_no_inprocess", url_prefix="/users_no_inprocess"),
    AdminRouteModule(route_cls=QidsView, name="qids", url_prefix="/qids"),
    AdminRouteModule(route_cls=QidsOthersView, name="qids_others", url_prefix="/qids_others"),
    AdminRouteModule(route_cls=CheckErrorsView, name="errors", url_prefix="/errors"),
]


def register_admin_blueprints(bp_admin: Blueprint) -> None:
    for module in ADMIN_ROUTE_MODULES:
        bp = Blueprint(module.name, __name__, url_prefix=module.url_prefix)
        module.route_cls(**module.extra_kwargs).register(bp)
        bp_admin.register_blueprint(bp)


__all__ = [
    "ADMIN_ROUTE_MODULES",
    "register_admin_blueprints",
]
