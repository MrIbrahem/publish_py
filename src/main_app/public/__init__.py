"""
Public Blueprints
"""

from flask import Flask

from .auth.routes import bp_auth
from .routes import (
    bp_api,
    bp_cxtoken,
    bp_fixrefs,
    bp_main,
    bp_publish,
    bp_td,
)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_td)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_cxtoken)
    app.register_blueprint(bp_publish)
    app.register_blueprint(bp_fixrefs)
    app.register_blueprint(bp_api)


__all__ = [
    "register_blueprints",
]
