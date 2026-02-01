"""Tests for app_routes.cxtoken module."""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask


@pytest.fixture
def app():
    """Create a test Flask application."""
    # Environment variables are set in conftest.py
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test_secret"

    # Import and register the blueprint
    from src.app_main.app_routes.cxtoken.routes import bp_cxtoken

    app.register_blueprint(bp_cxtoken)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestCxtokenEndpoint:
    """Tests for cxtoken endpoint."""

    def test_cors_not_allowed_without_origin(self, client):
        """Test that requests without allowed origin are rejected."""
        with patch("src.app_main.app_routes.cxtoken.routes.is_allowed") as mock_is_allowed:
            mock_is_allowed.return_value = None

            response = client.get("/?wiki=en&user=TestUser")

            assert response.status_code == 403
            assert b"Access denied" in response.data

    def test_returns_error_for_empty_params(self, client):
        """Test that error is returned for empty parameters."""
        with patch("src.app_main.app_routes.cxtoken.routes.is_allowed") as mock_is_allowed:
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            response = client.get("/")

            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
            assert data["error"]["code"] == "no data"

    def test_returns_error_for_missing_user(self, client):
        """Test that error is returned when user is missing."""
        with patch("src.app_main.app_routes.cxtoken.routes.is_allowed") as mock_is_allowed:
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            response = client.get("/?wiki=en")

            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data

    def test_returns_no_access_when_user_not_found(self, client):
        """Test that no access error is returned when user not found in DB."""
        with patch("src.app_main.app_routes.cxtoken.routes.is_allowed") as mock_is_allowed, \
             patch("src.app_main.app_routes.cxtoken.routes.get_user_token_by_username") as mock_get_token:
            mock_is_allowed.return_value = "medwiki.toolforge.org"
            mock_get_token.return_value = None

            response = client.get("/?wiki=en&user=UnknownUser")

            assert response.status_code == 403
            data = response.get_json()
            assert "error" in data
            assert data["error"]["code"] == "no access"

    def test_returns_cxtoken_on_success(self, client):
        """Test that cxtoken is returned on success."""
        with patch("src.app_main.app_routes.cxtoken.routes.is_allowed") as mock_is_allowed, \
             patch("src.app_main.app_routes.cxtoken.routes.get_user_token_by_username") as mock_get_token, \
             patch("src.app_main.app_routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken:
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            # Mock cxtoken response
            mock_get_cxtoken.return_value = {"cxtoken": "test_cx_token_123"}

            response = client.get("/?wiki=en&user=TestUser")

            assert response.status_code == 200
            data = response.get_json()
            assert "cxtoken" in data
            assert data["cxtoken"] == "test_cx_token_123"

    def test_handles_options_request(self, client):
        """Test that OPTIONS request is handled for CORS preflight."""
        with patch("src.app_main.app_routes.cxtoken.routes.is_allowed") as mock_is_allowed:
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            response = client.options("/")

            assert response.status_code == 200
            assert "Access-Control-Allow-Origin" in response.headers

    def test_deletes_access_on_invalid_authorization(self, client):
        """Test that access is deleted on invalid authorization error."""
        with patch("src.app_main.app_routes.cxtoken.routes.is_allowed") as mock_is_allowed, \
             patch("src.app_main.app_routes.cxtoken.routes.get_user_token_by_username") as mock_get_token, \
             patch("src.app_main.app_routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken, \
             patch("src.app_main.app_routes.cxtoken.routes.delete_user_token_by_username") as mock_delete:
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            # Mock invalid authorization error
            mock_get_cxtoken.return_value = {
                "csrftoken_data": {
                    "error": {"code": "mwoauth-invalid-authorization-invalid-user"}
                }
            }

            response = client.get("/?wiki=en&user=TestUser")

            # Verify delete was called
            mock_delete.assert_called_once()
            data = response.get_json()
            assert data.get("del_access") is True
