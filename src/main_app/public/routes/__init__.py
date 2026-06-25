"""
Flask public routes
"""

from flask import Flask

from ...admin.admin_panel import admin_route_module
from ..auth.routes import bp_auth
from .api.routes import bp_api
from .cxtoken.routes import bp_cxtoken
from .main import bp_main
from .publish.routes import bp_publish
from .refs.routes import bp_fixrefs
from .td import bp_leaderboard, bp_td


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_td)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_cxtoken)
    app.register_blueprint(bp_publish)
    app.register_blueprint(bp_fixrefs)
    app.register_blueprint(bp_api)

    app.register_blueprint(admin_route_module.bp)

__all__ = [
    "register_blueprints",
    "bp_api",
    "bp_auth",
    "bp_main",
    "bp_td",
    "bp_cxtoken",
    "bp_publish",
    "bp_fixrefs",
    "bp_leaderboard",
]
