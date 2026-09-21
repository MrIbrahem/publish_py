"""
Public Blueprints
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from flask import Blueprint, Flask

from ..extensions import csrf_exempt
from .auth.routes import AuthView
from .routes import (
    ApiRoutes,
    CxTokenRoutes,
    FixRefsRoutes,
    HtmltoSegmentsRoutes,
    LeaderBoardRoutes,
    MainRoutes,
    NewHtmlRoutes,
    PublishRoutes,
    TDRoutes,
    TranslateMedView,
)


@dataclass(frozen=True)
class PublicRouteModule:
    route_cls: type
    name: str
    url_prefix: str = ""
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


PUBLIC_ROUTE_MODULES: list[PublicRouteModule] = [
    PublicRouteModule(route_cls=NewHtmlRoutes, name="new_html", url_prefix="/new_html"),
    PublicRouteModule(route_cls=MainRoutes, name="main"),
    PublicRouteModule(route_cls=AuthView, name="auth", url_prefix="/auth"),
    PublicRouteModule(route_cls=ApiRoutes, name="api", url_prefix="/api"),
    PublicRouteModule(route_cls=CxTokenRoutes, name="cxtoken", url_prefix="/cxtoken"),
    PublicRouteModule(route_cls=FixRefsRoutes, name="fixrefs", url_prefix="/fixrefs"),
    PublicRouteModule(route_cls=TDRoutes, name="td", url_prefix="/Translation_Dashboard"),
    PublicRouteModule(route_cls=LeaderBoardRoutes, name="leaderboard", url_prefix="/Translation_Dashboard/leaderboard"),
    PublicRouteModule(
        route_cls=TranslateMedView, name="translate_med", url_prefix="/Translation_Dashboard/translate_med"
    ),
    PublicRouteModule(route_cls=PublishRoutes, name="publish", url_prefix="/publish"),
    PublicRouteModule(route_cls=HtmltoSegmentsRoutes, name="HtmltoSegments", url_prefix="/HtmltoSegments"),
]


class PublicRouteRegister:
    """Registers all route blueprints on a Flask app."""

    CSRF_EXEMPT_BPS = [
        "publish",
        "HtmltoSegments",
    ]

    @staticmethod
    def register(app: Flask) -> None:
        for module in PUBLIC_ROUTE_MODULES:
            bp = Blueprint(module.name, __name__, url_prefix=module.url_prefix)

            route_instance = module.route_cls()
            route_instance.register(bp=bp, **module.extra_kwargs)

            app.register_blueprint(bp)
            if module.name in PublicRouteRegister.CSRF_EXEMPT_BPS:
                csrf_exempt(app, bp)


__all__ = [
    "PublicRouteRegister",
]
