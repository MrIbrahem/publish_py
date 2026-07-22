"""
Public Blueprints
"""

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


def register_blueprints(app: Flask) -> None:
    bp_main = Blueprint("main", __name__)
    main_model = MainRoutes(Blueprint("main", __name__))

    bp_auth = Blueprint("auth", __name__, url_prefix="/auth")
    auth_model = AuthRoutes(bp_auth)

    bp_api = Blueprint("api", __name__, url_prefix="/api")
    api_model = ApiRoutes(bp_api)

    bp_cxtoken = Blueprint("cxtoken", __name__, url_prefix="/cxtoken")
    cx_model = CxTokenRoutes(bp_cxtoken)

    bp_td = Blueprint("td", __name__, url_prefix="/Translation_Dashboard")
    bp_leaderboard = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")

    leaderboard_model = LeaderBoardRoutes(bp_leaderboard)
    td_model = TDRoutes(bp_td)

    bp_td.register_blueprint(leaderboard_model.bp)

    publish_model = PublishRoutes(Blueprint("publish", __name__, url_prefix="/publish"))

    bp_fixrefs = Blueprint("fixrefs", __name__, url_prefix="/fixrefs")
    fixrefs_model = FixRefsRoutes(bp_fixrefs)

    app.register_blueprint(main_model.bp)
    app.register_blueprint(api_model.bp)
    app.register_blueprint(auth_model.bp)
    app.register_blueprint(td_model.bp)
    app.register_blueprint(cx_model.bp)

    app.register_blueprint(publish_model.bp)
    app.register_blueprint(fixrefs_model.bp)

    csrf_exempt(app, publish_model.bp)


__all__ = [
    "register_blueprints",
]
