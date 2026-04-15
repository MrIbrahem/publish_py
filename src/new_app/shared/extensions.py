"""
Flask extensions initialization.

This module centralizes Flask extensions to prevent circular imports
and enable proper initialization order with the application factory pattern.
"""

from flask import Flask
from flask_wtf.csrf import CSRFProtect

# Initialize extensions without binding to app
csrf = CSRFProtect()

# Future extensions can be added here:
# db = SQLAlchemy()
# login_manager = LoginManager()
# migrate = Migrate()


def csrf_init_app(app: Flask) -> None:
    # Initialize CSRF protection
    csrf.init_app(app)


def csrf_exempt(app, bp_publish) -> None:
    if app.config.get("WTF_CSRF_ENABLED"):
        csrf.exempt(bp_publish)


__all__ = [
    "csrf_init_app",
]
