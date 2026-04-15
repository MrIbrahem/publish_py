"""Flask application factory."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Tuple, Type

from flask import Flask, flash, render_template, request

from .app_routes import (
    bp_api,
    bp_auth,
    bp_cxtoken,
    bp_fixrefs,
    bp_main,
    bp_publish,
)
from .config import settings
from ..new_app.shared.cookies import CookieHeaderClient
from .db import ensure_qids_table
from .extensions import csrf
from .services import close_cached_db
from .services.users_services import ensure_user_token_table
from ..new_app.shared.auth.identity import current_user

logger = logging.getLogger(__name__)


def context_data() -> dict[str, Any]:
    user = current_user()
    return {
        "current_user": user,
        "is_authenticated": user is not None,
        "username": user.username if user else None,
        "oauth_enabled": bool(settings.oauth),
    }


def format_stage_timestamp(value: str) -> str:
    """Format ISO8601 like '2025-10-27T04:41:07' to 'Oct 27, 2025, 4:41 AM'."""
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        logger.exception("Failed to parse timestamp: %s", value)
        return ""
    # convert 24h → 12h with AM/PM
    hour24 = dt.hour
    ampm = "AM" if hour24 < 12 else "PM"
    hour12 = hour24 % 12 or 12
    minute = f"{dt.minute:02d}"
    month = dt.strftime("%b")  # Oct
    return f"{month} {dt.day}, {dt.year}, {hour12}:{minute} {ampm}"


def create_app(config_class: Type | None = None) -> Flask:
    """Instantiate and configure the Flask application.

    Args:
        config_class: Optional configuration class to use. If not provided,
                     uses environment-based settings.

    Returns:
        Configured Flask application instance.

    Example:
        from app_main import create_app
        from app_main.config import TestingConfig
        app = create_app(TestingConfig)
    """
    # Use absolute paths based on the current module location
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, "..", "templates")
    static_dir = os.path.join(base_dir, "..", "static")

    # app = Flask(
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )
    app.url_map.strict_slashes = False
    app.test_client_class = CookieHeaderClient

    # Load configuration
    if config_class is not None:
        # Use provided config class (Flask-style)
        app.config.from_object(config_class())
    else:
        # Use environment-based settings (legacy behavior)
        app.secret_key = settings.secret_key
        app.config.update(
            SESSION_COOKIE_HTTPONLY=settings.cookie.httponly,
            SESSION_COOKIE_SECURE=settings.cookie.secure,
            SESSION_COOKIE_SAMESITE=settings.cookie.samesite,
        )

    oauth_enabled = settings.oauth and settings.oauth.enabled
    app.config["USE_MW_OAUTH"] = oauth_enabled

    # Initialize CSRF protection
    csrf.init_app(app)

    if oauth_enabled and settings.database_data.db_host:
        ensure_user_token_table()
        ensure_qids_table(settings.database_data)

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_cxtoken)
    app.register_blueprint(bp_publish)
    app.register_blueprint(bp_fixrefs)
    app.register_blueprint(bp_api)

    if app.config.get("WTF_CSRF_ENABLED"):
        csrf.exempt(bp_publish)

    @app.context_processor
    def _inject_data():  # pragma: no cover - trivial wrapper
        return context_data()

    app.jinja_env.globals.setdefault("USE_MW_OAUTH", oauth_enabled)
    app.jinja_env.filters["format_stage_timestamp"] = format_stage_timestamp

    @app.teardown_appcontext
    def _cleanup_connections(exception: Exception | None) -> None:  # pragma: no cover - teardown
        close_cached_db()

    @app.errorhandler(404)
    def page_not_found(e: Exception) -> Tuple[str, int]:
        """Handle 404 errors"""
        logger.error("Page not found: %s", e)
        logger.error(f"Request host: {request.host}")
        flash("Page not found", "warning")
        return render_template("index.html", title="Page Not Found"), 404

    @app.errorhandler(500)
    def internal_server_error(e: Exception) -> Tuple[str, int]:
        """Handle 500 errors"""
        logger.error("Internal Server Error: %s", e)
        flash("Internal Server Error", "danger")
        return render_template("index.html", title="Internal Server Error"), 500

    # Add cache control headers to prevent CSRF token caching issues
    @app.after_request
    def add_cache_headers(response):
        """Prevent CSRF token caching on form-related routes."""
        endpoints = ["auth.", "publish.", "fixrefs.", "cxtoken."]
        if request.endpoint and any(request.endpoint.startswith(bp) for bp in endpoints):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    return app
