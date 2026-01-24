
from .auth.routes import bp_auth
from .main.routes import bp_main
from .cxtoken_routes import bp_cxtoken
from .post_routes import bp_post

__all__ = [
    "bp_auth",
    "bp_main",
    "bp_cxtoken",
    "bp_post",
]
