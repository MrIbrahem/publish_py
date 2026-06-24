"""
Flask public routes
"""

from .api.routes import bp_api
from .auth.routes import bp_auth
from .cxtoken.routes import bp_cxtoken
from .main import bp_main
from .publish.routes import bp_publish
from .refs.routes import bp_fixrefs
from .td import bp_leaderboard, bp_td

__all__ = [
    "bp_api",
    "bp_auth",
    "bp_main",
    "bp_td",
    "bp_cxtoken",
    "bp_publish",
    "bp_fixrefs",
]
