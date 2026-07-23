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
)

@dataclass(frozen=True)
class PublicRouteModule:
    route_cls: type
    name: str
    url_prefix: str
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


PUBLIC_ROUTE_MODULES: list[PublicRouteModule] = [
    PublicRouteModule(MainRoutes, "main", ""),
    PublicRouteModule(AuthRoutes, "auth", "/auth"),
    PublicRouteModule(ApiRoutes, "api", "/api"),
    PublicRouteModule(CxTokenRoutes, "cxtoken", "/cxtoken"),
    PublicRouteModule(FixRefsRoutes, "fixrefs", "/fixrefs"),
]


def register_blueprints(app: Flask) -> None:
    for module in PUBLIC_ROUTE_MODULES:
        bp = Blueprint(module.name, __name__, url_prefix=module.url_prefix)
        route_instance = module.route_cls(bp=bp, **module.extra_kwargs)
        app.register_blueprint(route_instance.bp)

    bp_leaderboard = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")
    leaderboard_model = LeaderBoardRoutes(bp_leaderboard)

    bp_td = Blueprint("td", __name__, url_prefix="/Translation_Dashboard")
    td_model = TDRoutes(bp_td)

    bp_td.register_blueprint(leaderboard_model.bp)

    publish_model = PublishRoutes(Blueprint("publish", __name__, url_prefix="/publish"))

    app.register_blueprint(td_model.bp)
    app.register_blueprint(publish_model.bp)

    csrf_exempt(app, publish_model.bp)


__all__ = [
    "register_blueprints",
]
