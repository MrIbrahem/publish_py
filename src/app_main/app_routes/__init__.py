from .api.routes import bp_api
from .auth.routes import bp_auth
from .cxtoken.routes import bp_cxtoken
from .main.routes import bp_main
from .post.routes import bp_post

__all__ = [
    "bp_api",
    "bp_auth",
    "bp_main",
    "bp_cxtoken",
    "bp_post",
]
