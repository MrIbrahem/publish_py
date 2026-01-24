
from .auth.routes import bp_auth
from .main.routes import bp_main
from .token_routes import bp_token
from .post_routes import bp_post

__all__ = [
    "bp_auth",
    "bp_main",
    "bp_token",
    "bp_post",
]
