"""Tests for app_routes.cxtoken module."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient


@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    # Environment variables are set in conftest.py
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.secret_key = "test_secret"
    app.config["TESTING"] = True
    app.config["CORS_DISABLED"] = True

    # Import and register the blueprint
    from src.app_main.public.routes.cxtoken.routes import bp_cxtoken

    app.register_blueprint(bp_cxtoken)
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client."""
    return app.test_client()


class TestCxtokenEndpoint:
    """Tests for cxtoken endpoint."""

    def test_cors_not_allowed_without_origin(self, client):

        with (patch("src.app_main.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token,):
            mock_get_token.return_value = None

            """Test that requests without allowed origin are rejected."""
            response = client.get(
                "/cxtoken?wiki=en&user=TestUser",
                base_url="https://unknown-site.com",
            )

            assert response.status_code == 403

    def test_returns_error_for_empty_params(self, client):
        """Test that error is returned for empty parameters."""

        response = client.get("/cxtoken")

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"]["code"] == "no data"

    def test_returns_error_for_missing_user(self, client):
        """Test that error is returned when user is missing."""

        response = client.get("/cxtoken?wiki=en")

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_returns_no_access_when_user_not_found(self, client):
        """Test that no access error is returned when user not found in DB."""
        with (patch("src.app_main.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token,):
            mock_get_token.return_value = None

            response = client.get("/cxtoken?wiki=en&user=UnknownUser")

            assert response.status_code == 403
            data = response.get_json()
            assert isinstance(data, dict)

            assert "error" in data
            assert isinstance(data["error"], dict)
            assert data["error"]["code"] == "no access"

    def test_returns_cxtoken_on_success(self, client):
        """Test that cxtoken is returned on success."""
        with (
            patch("src.app_main.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.public.routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken,
        ):

            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            # Mock cxtoken response
            mock_get_cxtoken.return_value = {"cxtoken": "test_cx_token_123"}

            response = client.get("/cxtoken?wiki=en&user=TestUser")

            assert response.status_code == 200
            data = response.get_json()
            assert "cxtoken" in data
            assert data["cxtoken"] == "test_cx_token_123"

    def test_handles_options_request(self, client):
        """Test that OPTIONS request is handled for CORS preflight."""
        response = client.options(
            "/cxtoken",
            base_url="https://medwiki.toolforge.org",
            headers={"Origin": "https://medwiki.toolforge.org"},
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers

    def test_deletes_access_on_invalid_authorization(self, client):
        """Test that access is deleted on invalid authorization error."""
        with (
            patch("src.app_main.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.public.routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken,
            patch("src.app_main.public.routes.cxtoken.routes.delete_user_token_by_username") as mock_delete,
        ):
            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            # Mock invalid authorization error
            mock_get_cxtoken.return_value = {
                "csrftoken_data": {"error": {"code": "mwoauth-invalid-authorization-invalid-user"}}
            }

            response = client.get("/cxtoken?wiki=en&user=TestUser")

            # Verify delete was called
            mock_delete.assert_called_once()
            data = response.get_json()
            assert data == {"error": {"code": "no access", "info": "no access"}, "username": "TestUser"}
