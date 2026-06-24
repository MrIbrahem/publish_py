"""
Flask application factory.
"""

from __future__ import annotations

import logging
import os
from datetime import date, timedelta
from typing import Any, Tuple, Type

from flask import Flask, Response, flash, jsonify, render_template, request  # , g

from .admin.admin_panel import admin_route_module
from .db import init_db
from .db.services.users import active_coordinators
from .public.routes import (
    bp_api,
    bp_auth,
    bp_cxtoken,
    bp_fixrefs,
    bp_main,
    bp_publish,
    bp_td,
)
from .shared.auth.identity import current_user
from .shared.core.cookies import CookieHeaderClient
from .shared.core.extensions import csrf_exempt, csrf_init_app
from .shared.core.extensions import db as _db
from .shared.core.extensions import migrate
from .shared.core.jinja_filters import filters

logger = logging.getLogger(__name__)


def context_data() -> dict[str, Any]:
    """
    used in @app.context_processor
    """
    user = current_user()
    return {
        "current_user": user,
        "is_authenticated": user is not None,
        "is_admin": bool(user and user.username in active_coordinators()),
        "username": user.username if user else None,
        "yesterday": (date.today() - timedelta(days=1)).isoformat(),
    }


def create_app(config_class: Type) -> Flask:
    """Instantiate and configure the Flask application.

    Args:
        config_class: configuration class to use.

    Returns:
        Configured Flask application instance.
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
    # Use provided config class (Flask-style)
    app.config.from_object(config_class())

    # Initialize CSRF protection
    csrf_init_app(app)

    # Initialize Flask-SQLAlchemy (new)
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        _db.init_app(app)
        migrate.init_app(app, _db)

        with app.app_context():
            # Create database tables and views if they don't exist
            init_db(_db)

    # if settings.database_data.db_host:
    # db_url = build_db_url(settings.database_data.to_dict())

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_td)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_cxtoken)
    app.register_blueprint(bp_publish)
    app.register_blueprint(bp_fixrefs)
    app.register_blueprint(bp_api)
    app.register_blueprint(admin_route_module.bp)

    csrf_exempt(app, bp_publish)

    @app.context_processor
    def _inject_data():  # pragma: no cover - trivial wrapper
        return context_data()

    app.jinja_env.filters.update(filters)

    # @app.teardown_appcontext
    # def _cleanup_connections(exception: Exception | None) -> None:  # pragma: no cover - teardown

    @app.errorhandler(400)
    def bad_request(e: Exception) -> Tuple[str | Response, int]:
        """Handle 400 errors"""
        logger.warning("Bad request: %s", e)
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Bad request", "message": str(e)}), 400

        flash("Bad request", "warning")
        return render_template("index.html", title="Bad Request"), 400

    @app.errorhandler(401)
    def unauthorized(e: Exception) -> Tuple[str | Response, int]:
        """Handle 401 errors"""
        logger.warning("Unauthorized: %s", e)
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
        flash("Please log in to access this page", "warning")
        return render_template("index.html", title="Unauthorized"), 401

    @app.errorhandler(403)
    def forbidden(e: Exception) -> Tuple[str | Response, int]:
        """Handle 403 errors"""
        logger.warning("Forbidden: %s", e)
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Forbidden", "message": "Access denied"}), 403
        flash("Access denied", "danger")
        return render_template("index.html", title="Access Denied"), 403

    @app.errorhandler(404)
    def page_not_found(e: Exception) -> Tuple[str | Response, int]:
        """Handle 404 errors"""
        logger.error("Page not found: %s", e)
        logger.error(f"Request url: {request.url}")
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Not found", "message": str(e)}), 404
        flash("Page not found", "warning")
        return render_template("index.html", title="Page Not Found"), 404

    @app.errorhandler(429)
    def too_many_requests(e: Exception) -> Tuple[str | Response, int]:
        """Handle 429 rate limit errors"""
        logger.warning("Rate limit exceeded: %s", e)
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Too many requests", "message": "Rate limit exceeded"}), 429
        flash("Too many requests. Please try again later.", "warning")
        return render_template("index.html", title="Rate Limit Exceeded"), 429

    @app.errorhandler(500)
    def internal_server_error(e: Exception) -> Tuple[str | Response, int]:
        """Handle 500 errors"""
        logger.error("Internal Server Error: %s", e)
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
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

    # g.settings = settings  # Make settings available in Flask's global context
    return app


__all__ = [
    "context_data",
    "create_app",
]
