"""
Flask public routes
"""

from flask import Blueprint
from .api.routes import bp_api
from .auth.routes import bp_auth
from .cxtoken.routes import bp_cxtoken
from .main import bp_leaderboard, bp_main, bp_td
from .publish.routes import bp_publish
from .refs.routes import bp_fixrefs


def register_td_blueprints(bp_td: Blueprint) -> None:
    bp_td.register_blueprint(bp_leaderboard)


register_td_blueprints(bp_td)


__all__ = [
    "bp_api",
    "bp_auth",
    "bp_main",
    "bp_td",
    "bp_cxtoken",
    "bp_publish",
    "bp_fixrefs",
]
