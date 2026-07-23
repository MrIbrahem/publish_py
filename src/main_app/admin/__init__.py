"""Admin blueprint package."""

from flask import Blueprint, Flask

from .admin_panel import AdminPanel
from .routes import ADMIN_ROUTE_MODULES


def register_admin_blueprints(bp_admin: Blueprint) -> None:
    for module in ADMIN_ROUTE_MODULES:
        bp = Blueprint(module.name, __name__, url_prefix=module.url_prefix, **module.extra_kwargs)
        route_instance = module.route_cls(bp)
        bp_admin.register_blueprint(route_instance.bp)


def register_bp_admin_blueprints(app: Flask) -> None:
    bp_admin = Blueprint("admin", __name__, url_prefix="/admin")
    admin_model = AdminPanel(bp_admin)

    register_admin_blueprints(bp_admin)

    app.register_blueprint(admin_model.bp)


__all__ = [
    "register_bp_admin_blueprints",
]
