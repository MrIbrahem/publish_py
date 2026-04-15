"""
Flask public routes
"""

from ....app_main.app_routes.api.routes import bp_api
from ....app_main.app_routes.auth.routes import bp_auth
from ....app_main.app_routes.cxtoken.routes import bp_cxtoken
from ....app_main.app_routes.main.routes import bp_main
from ....app_main.app_routes.publish.routes import bp_publish
from ....app_main.app_routes.refs.routes import bp_fixrefs

__all__ = [
    "bp_api",
    "bp_auth",
    "bp_main",
    "bp_cxtoken",
    "bp_publish",
    "bp_fixrefs",
]
