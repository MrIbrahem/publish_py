"""
Public Blueprints
"""

from dataclasses import dataclass, field
from typing import Any

from flask import Blueprint, Flask

from ..extensions import csrf_exempt
from .auth.routes import AuthRoutes
from .routes import (
    ApiRoutes,
    CxTokenRoutes,
    FixRefsRoutes,
    LeaderBoardRoutes,
    MainRoutes,
    PublishRoutes,
    TDRoutes,
    HtmltoSegmentsRoutes,
)


@dataclass(frozen=True)
class PublicRouteModule:
    route_cls: type
    name: str
    url_prefix: str = ""
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


PUBLIC_ROUTE_MODULES: list[PublicRouteModule] = [
    # PublicRouteModule(HtmltoSegmentsRoutes, "HtmltoSegments", "/HtmltoSegments"),
    PublicRouteModule(MainRoutes, "main"),
    PublicRouteModule(AuthRoutes, "auth", "/auth"),
    PublicRouteModule(ApiRoutes, "api", "/api"),
    PublicRouteModule(CxTokenRoutes, "cxtoken", "/cxtoken"),
    PublicRouteModule(FixRefsRoutes, "fixrefs", "/fixrefs"),
    PublicRouteModule(TDRoutes, "td", "/Translation_Dashboard"),
    PublicRouteModule(LeaderBoardRoutes, "leaderboard", "/Translation_Dashboard/leaderboard"),
]


class RouteRegistrar:
    """Registers all route blueprints on a Flask app."""

    @staticmethod
    def register(app: Flask):
        for module in PUBLIC_ROUTE_MODULES:
            bp = Blueprint(module.name, __name__, url_prefix=module.url_prefix)
            route_instance = module.route_cls(bp=bp, **module.extra_kwargs)
            app.register_blueprint(route_instance.bp)

        publish_model = PublishRoutes(Blueprint("publish", __name__, url_prefix="/publish"))
        app.register_blueprint(publish_model.bp)
        csrf_exempt(app, publish_model.bp)

        htmltosegments_model = HtmltoSegmentsRoutes(Blueprint("HtmltoSegments", __name__, url_prefix="/HtmltoSegments"))
        app.register_blueprint(htmltosegments_model.bp)
        csrf_exempt(app, htmltosegments_model.bp)


__all__ = [
    "RouteRegistrar",
]
