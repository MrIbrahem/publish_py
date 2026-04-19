"""Admin-only routes for managing coordinator access."""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)

from .coordinators import Coordinators

# from ..admin_routes import (
#     Coordinators,
#     Jobs,
#     OwidCharts,
#     Templates,
# )
from ..decorators import admin_required
from .full_translators import FullTranslators
from .language_settings import LanguageSettings
from .settings import SettingsRoutes
from ..sidebar import create_side
from .users_no_inprocess import UsersNoInprocess

logger = logging.getLogger(__name__)

bp_admin = Blueprint("admin", __name__, url_prefix="/admin")


@bp_admin.app_context_processor
def inject_sidebar():
    path_parts = request.path.strip("/").split("/")
    active_route = path_parts[1] if len(path_parts) > 1 else ""
    # logger.debug(f"Injecting sidebar for path='{request.path}'")
    sidebar_html = create_side(active_route=active_route)
    return {"sidebar": sidebar_html}


@bp_admin.get("/")
@admin_required
def index():
    return render_template("admins/index.html")


def register_blueprints(bp_admin) -> None:
    Coordinators(bp_admin)
    FullTranslators(bp_admin)
    UsersNoInprocess(bp_admin)
    LanguageSettings(bp_admin)
    # Templates(bp_admin)
    SettingsRoutes(bp_admin)
    # Jobs(bp_admin)
    # OwidCharts(bp_admin)


register_blueprints(bp_admin)
