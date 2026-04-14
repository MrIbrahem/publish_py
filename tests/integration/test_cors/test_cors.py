"""Tests for cors module."""

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

    # Generate encryption key if not set
    from cryptography.fernet import Fernet

    if not os.environ.get("OAUTH_ENCRYPTION_KEY"):
        os.environ["OAUTH_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config["TESTING"] = True
    app.config["CORS_DISABLED"] = False
    return app


class TestIsAllowed:
    @pytest.mark.parametrize("headers, expected", [
        ({"Origin": "https://medwiki.toolforge.org"}, "medwiki.toolforge.org"),
        ({"Referer": "https://mdwikicx.toolforge.org/page"}, "mdwikicx.toolforge.org"),
        ({"Origin": "https://evil.com", "Referer": "https://evil.com"}, None),
        ({}, None),
    ])
    def test_is_allowed(self, app, headers, expected):
        from src.app_main.cors import is_allowed

        with app.test_request_context(headers=headers):
            from flask import request
            result = is_allowed(request)
            assert result == expected
