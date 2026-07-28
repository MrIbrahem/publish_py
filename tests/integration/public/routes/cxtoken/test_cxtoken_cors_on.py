"""
Tests for check_cors on cxtoken routes
with CORS_ENABLED (CORS_DISABLED=False).
"""

import os
from unittest.mock import patch

import pytest
from flask import Blueprint, Flask
from flask.testing import FlaskClient

from src.main_app.config import TestingConfig
from src.main_app.db.services import UsersService, UserTokenService

ALLOWED_DOMAIN = "medwiki.toolforge.org"


@pytest.fixture
def mock_app(sqlite_db) -> Flask:
    """Create a test Flask application with CORS enabled."""

    os.environ.setdefault("CORS_ALLOWED_DOMAINS", f"{ALLOWED_DOMAIN},mdwikicx.toolforge.org")

    mock_app = Flask(__name__)
    mock_app.url_map.strict_slashes = False
    mock_app.config.from_object(TestingConfig)
    mock_app.config.update({"CORS_DISABLED": False})

    sqlite_db.init_app(mock_app)

    from src.main_app.public.routes.cxtoken.routes import CxTokenRoutes

    bp_cxtoken = Blueprint("cxtoken", __name__, url_prefix="/cxtoken")
    cx_model = CxTokenRoutes(bp_cxtoken)

    mock_app.register_blueprint(cx_model.bp)
    return mock_app


@pytest.fixture
def mock_client(mock_app: Flask) -> FlaskClient:
    """Create a test client."""
    return mock_app.test_client()


class TestCheckCorsOnCxtokenGet:
    """Tests for @check_cors decorator on cxtoken GET route with CORS_ENABLED."""

    def test_get_disallowed_origin_returns_403(self, mock_is_denied, mock_client):
        """GET from disallowed origin returns 403."""
        response = mock_client.get(
            "/cxtoken?wiki=en&user=TestUser",
            headers={"Origin": "https://evil.com"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"]["code"] == "access_denied"
        assert "authorized domains" in data["error"]["info"]

    def test_get_allowed_origin_proceeds(self, mock_is_allowed_medwiki, mock_client):
        """GET from allowed origin passes CORS check and reaches handler."""
        response = mock_client.get(
            "/cxtoken?wiki=en&user=UnknownUser",
            headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"]["code"] == "no access"
        assert response.headers.get("Access-Control-Allow-Origin") == f"https://{ALLOWED_DOMAIN}"

    def test_get_no_origin_returns_403(self, mock_is_denied, mock_client):
        """GET with no Origin header returns 403."""
        response = mock_client.get("/cxtoken?wiki=en&user=TestUser")
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"]["code"] == "access_denied"

    def test_get_allowed_origin_returns_cxtoken(self, mock_is_allowed_medwiki, mock_client):
        """GET from allowed origin returns cxtoken on success."""
        users_service = UsersService()
        user = users_service.create_user("CorsTokenUser")

        token_service = UserTokenService()
        encrypted_token = token_service.encrypt_value("test_access_token")
        encrypted_secret = token_service.encrypt_value("test_access_secret")
        token_service.create_user_token(user.user_id, encrypted_token, encrypted_secret)

        with patch("src.main_app.public.routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken:
            mock_get_cxtoken.return_value = {"cxtoken": "test_cx_token_123"}

            response = mock_client.get(
                "/cxtoken?wiki=en&user=CorsTokenUser",
                headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert "cxtoken" in data
            assert data["cxtoken"] == "test_cx_token_123"


class TestCheckCorsOnCxtokenOptions:
    """Tests for @check_cors decorator on cxtoken OPTIONS route with CORS_ENABLED."""

    def test_options_allowed_origin_returns_200(self, mock_is_allowed_medwiki, mock_client):
        """OPTIONS preflight from allowed origin returns 200 with CORS headers."""
        response = mock_client.options(
            "/cxtoken",
            headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == f"https://{ALLOWED_DOMAIN}"

    def test_options_disallowed_origin_returns_403(self, mock_is_denied, mock_client):
        """OPTIONS preflight from disallowed origin returns 403."""
        response = mock_client.options(
            "/cxtoken",
            headers={"Origin": "https://evil.com"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"]["code"] == "access_denied"

    def test_options_no_origin_returns_403(self, mock_is_denied, mock_client):
        """OPTIONS preflight with no Origin header returns 403."""
        response = mock_client.options("/cxtoken")
        assert response.status_code == 403


class TestCxtokenCorsOnIntegration:
    """Integration tests using real is_allowed behavior with CORS_ENABLED."""

    def test_get_same_origin_passes_real_cors(self, mock_app, mock_client):
        """GET from same origin passes real CORS check."""
        response = mock_client.get(
            "/cxtoken?wiki=en&user=UnknownUser",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"]["code"] == "no access"

    def test_get_disallowed_origin_blocked_real_cors(self, mock_app, mock_client):
        """GET from disallowed origin is blocked by real CORS check."""
        response = mock_client.get(
            "/cxtoken?wiki=en&user=TestUser",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": "https://evil.com"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"]["code"] == "access_denied"

    def test_options_same_origin_passes_real_cors(self, mock_app, mock_client):
        """OPTIONS from same origin passes real CORS check."""
        response = mock_client.options(
            "/cxtoken",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers

    def test_options_from_allowed_cross_origin_passes_real_cors(self, mock_app, mock_client):
        """OPTIONS from allowed cross-origin domain passes real CORS check."""
        response = mock_client.options(
            "/cxtoken",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": "https://mdwikicx.toolforge.org"},
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers
