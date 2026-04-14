"""
Tests for app_routes.post module.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask


@pytest.fixture
def app():
    """Create a test Flask application."""
    import os

    os.environ.setdefault("FLASK_SECRET_KEY", "test_secret_key_12345678901234567890")
    os.environ.setdefault("OAUTH_MWURI", "https://en.wikipedia.org/w/index.php")
    os.environ.setdefault("OAUTH_CONSUMER_KEY", "test")
    os.environ.setdefault("OAUTH_CONSUMER_SECRET", "test")
    os.environ.setdefault("CORS_ALLOWED_DOMAINS", "medwiki.toolforge.org,mdwikicx.toolforge.org")

    from cryptography.fernet import Fernet

    if not os.environ.get("OAUTH_ENCRYPTION_KEY"):
        os.environ["OAUTH_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.secret_key = "test_secret"

    app.config["TESTING"] = True
    app.config["CORS_DISABLED"] = False

    from src.app_main.app_routes.publish.routes import bp_publish

    app.register_blueprint(bp_publish)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()
