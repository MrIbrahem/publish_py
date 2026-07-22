"""
Public Blueprints
"""

from flask import Blueprint, Flask

from .auth.routes import AuthRoutes
from .routes import (
    ApiRoutes,
    CxTokenRoutes,
    LeaderBoardRoutes,
    MainRoutes,
    TDRoutes,
    bp_fixrefs,
    bp_publish,
)


def register_blueprints(app: Flask) -> None:
    bp_main = Blueprint("main", __name__)
    main_model = MainRoutes(bp_main)

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

    app.register_blueprint(main_model.bp)
    app.register_blueprint(api_model.bp)
    app.register_blueprint(auth_model.bp)
    app.register_blueprint(td_model.bp)
    app.register_blueprint(cx_model.bp)
    app.register_blueprint(bp_publish)
    app.register_blueprint(bp_fixrefs)


__all__ = [
    "register_blueprints",
]
