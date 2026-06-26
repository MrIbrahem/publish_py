"""Tests for app_routes.cxtoken module."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.main_app.config import TestingConfig


@pytest.fixture
def mock_app() -> Flask:
    """Create a test Flask application."""
    # Environment variables are set in conftest.py
    mock_app = Flask(__name__)
    mock_app.url_map.strict_slashes = False
    mock_app.secret_key = "test_secret"
    mock_app.config.from_object(TestingConfig)

    from src.main_app.extensions import db

    db.init_app(mock_app)

    # Import and register the blueprint
    from src.main_app.public.routes.cxtoken.routes import bp_cxtoken

    mock_app.register_blueprint(bp_cxtoken)
    return mock_app


@pytest.fixture
def mock_client(mock_app: Flask) -> FlaskClient:
    """Create a test client."""
    return mock_app.test_client()


class TestCxtokenEndpoint:
    """Tests for cxtoken endpoint."""

    def test_cors_not_allowed_without_origin(self, mock_client):
        """Test that requests without allowed origin are rejected."""
        with patch("src.main_app.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token:
            mock_get_token.return_value = None
            response = mock_client.get(
                "/cxtoken?wiki=en&user=TestUser",
                base_url="https://unknown-site.com",
            )
            assert response.status_code == 403

    def test_returns_error_for_empty_params(self, mock_client):
        """Test that error is returned for empty parameters."""

        response = mock_client.get("/cxtoken")

        assert response.status_code == 400
        data = response.get_json()
        assert data == {
            "error": {
                "code": "validation_error",
                "info": {
                    "user": [
                        "Missing data for required field.",
                    ],
                    "wiki": [
                        "Missing data for required field.",
                    ],
                },
            },
        }

    def test_returns_error_for_missing_user(self, mock_client):
        """Test that error is returned when user is missing."""

        response = mock_client.get("/cxtoken?wiki=en")

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_returns_no_access_when_user_not_found(self, mock_client):
        """Test that no access error is returned when user not found in DB."""
        with (patch("src.main_app.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token,):
            mock_get_token.return_value = None

            response = mock_client.get("/cxtoken?wiki=en&user=UnknownUser")

            assert response.status_code == 403
            data = response.get_json()
            assert isinstance(data, dict)
            assert "error" in data
            assert isinstance(data["error"], dict)

            assert data == {
                "error": {
                    "code": "no access",
                    "info": "no access",
                },
                "username": "UnknownUser",
            }

    def test_returns_cxtoken_on_success(self, mock_client):
        """Test that cxtoken is returned on success."""
        with (
            patch("src.main_app.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token,
            patch("src.main_app.public.routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken,
        ):
            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            # Mock cxtoken response
            mock_get_cxtoken.return_value = {"cxtoken": "test_cx_token_123"}

            response = mock_client.get("/cxtoken?wiki=en&user=TestUser")

            assert response.status_code == 200
            data = response.get_json()
            assert "cxtoken" in data
            assert data["cxtoken"] == "test_cx_token_123"

    def test_handles_options_request(self, mock_client):
        """Test that OPTIONS request is handled for CORS preflight."""
        response = mock_client.options(
            "/cxtoken",
            base_url="https://medwiki.toolforge.org",
            headers={"Origin": "https://medwiki.toolforge.org"},
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers

    def test_deletes_access_on_invalid_authorization(self, mock_client):
        """Test that access is deleted on invalid authorization error."""
        with (
            patch("src.main_app.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token,
            patch("src.main_app.public.routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken,
            patch("src.main_app.public.routes.cxtoken.routes.delete_user_token") as mock_delete,
        ):
            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            # Mock invalid authorization error
            mock_get_cxtoken.return_value = {
                "csrftoken_data": {"error": {"code": "mwoauth-invalid-authorization-invalid-user"}}
            }

            response = mock_client.get("/cxtoken?wiki=en&user=TestUser")

            # Verify delete was called
            mock_delete.assert_called_once()
            data = response.get_json()
            assert data == {"error": {"code": "no access", "info": "no access"}, "username": "TestUser"}
