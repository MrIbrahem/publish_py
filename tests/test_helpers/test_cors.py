"""Tests for helpers.cors module."""

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
    app.config["TESTING"] = True
    return app


class TestIsAllowed:
    """Tests for is_allowed function."""

    def test_allows_medwiki_origin(self, app):
        """Test that medwiki.toolforge.org origin is allowed."""
        with app.test_request_context(
            headers={"Origin": "https://medwiki.toolforge.org"}
        ):
            from src.app.helpers.cors import is_allowed

            result = is_allowed()
            assert result == "medwiki.toolforge.org"

    def test_allows_mdwikicx_referer(self, app):
        """Test that mdwikicx.toolforge.org referer is allowed."""
        with app.test_request_context(
            headers={"Referer": "https://mdwikicx.toolforge.org/page"}
        ):
            from src.app.helpers.cors import is_allowed

            result = is_allowed()
            assert result == "mdwikicx.toolforge.org"

    def test_rejects_unknown_origin(self, app):
        """Test that unknown origin is rejected."""
        with app.test_request_context(
            headers={"Origin": "https://evil.com", "Referer": "https://evil.com"}
        ):
            from src.app.helpers.cors import is_allowed

            result = is_allowed()
            assert result is None

    def test_rejects_empty_headers(self, app):
        """Test that empty headers are rejected."""
        with app.test_request_context():
            from src.app.helpers.cors import is_allowed

            result = is_allowed()
            assert result is None
