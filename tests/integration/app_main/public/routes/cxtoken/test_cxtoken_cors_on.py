"""
Tests for check_cors on cxtoken routes
with CORS_ENABLED (CORS_DISABLED=False).
"""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

ALLOWED_DOMAIN = "medwiki.toolforge.org"


@pytest.fixture
def app() -> Flask:
    """Create a test Flask application with CORS enabled."""
    import os

    os.environ.setdefault("CORS_ALLOWED_DOMAINS", f"{ALLOWED_DOMAIN},mdwikicx.toolforge.org")

    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.secret_key = "test_secret"

    app.config["TESTING"] = True
    app.config["CORS_DISABLED"] = False

    from src.app_main.public.routes.cxtoken.routes import bp_cxtoken

    app.register_blueprint(bp_cxtoken)
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client."""
    return app.test_client()


class TestCheckCorsOnCxtokenGet:
    """Tests for @check_cors decorator on cxtoken GET route with CORS_ENABLED."""

    def test_get_disallowed_origin_returns_403(self, client):
        """GET from disallowed origin returns 403."""
        with patch("src.app_main.shared.core.cors.is_allowed", return_value=None):
            response = client.get(
                "/cxtoken?wiki=en&user=TestUser",
                headers={"Origin": "https://evil.com"},
            )
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "access_denied"
            assert "authorized domains" in data["error"]["info"]

    def test_get_allowed_origin_proceeds(self, client):
        """GET from allowed origin passes CORS check and reaches handler."""
        with (
            patch("src.app_main.shared.core.cors.is_allowed", return_value=ALLOWED_DOMAIN),
            patch(
                "src.app_main.public.routes.cxtoken.routes.get_user_token_by_username",
                return_value=None,
            ),
        ):
            response = client.get(
                "/cxtoken?wiki=en&user=UnknownUser",
                headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
            )
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "no access"
            assert response.headers.get("Access-Control-Allow-Origin") == f"https://{ALLOWED_DOMAIN}"

    def test_get_no_origin_returns_403(self, client):
        """GET with no Origin header returns 403."""
        with patch("src.app_main.shared.core.cors.is_allowed", return_value=None):
            response = client.get("/cxtoken?wiki=en&user=TestUser")
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "access_denied"

    def test_get_allowed_origin_returns_cxtoken(self, client):
        """GET from allowed origin returns cxtoken on success."""
        with (
            patch("src.app_main.shared.core.cors.is_allowed", return_value=ALLOWED_DOMAIN),
            patch("src.app_main.public.routes.cxtoken.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.public.routes.cxtoken.routes.get_cxtoken") as mock_get_cxtoken,
        ):
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token
            mock_get_cxtoken.return_value = {"cxtoken": "test_cx_token_123"}

            response = client.get(
                "/cxtoken?wiki=en&user=TestUser",
                headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert "cxtoken" in data
            assert data["cxtoken"] == "test_cx_token_123"


class TestCheckCorsOnCxtokenOptions:
    """Tests for @check_cors decorator on cxtoken OPTIONS route with CORS_ENABLED."""

    def test_options_allowed_origin_returns_200(self, client):
        """OPTIONS preflight from allowed origin returns 200 with CORS headers."""
        with patch("src.app_main.shared.core.cors.is_allowed", return_value=ALLOWED_DOMAIN):
            response = client.options(
                "/cxtoken",
                headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
            )
            assert response.status_code == 200
            assert "Access-Control-Allow-Methods" in response.headers
            assert response.headers["Access-Control-Allow-Origin"] == f"https://{ALLOWED_DOMAIN}"

    def test_options_disallowed_origin_returns_403(self, client):
        """OPTIONS preflight from disallowed origin returns 403."""
        with patch("src.app_main.shared.core.cors.is_allowed", return_value=None):
            response = client.options(
                "/cxtoken",
                headers={"Origin": "https://evil.com"},
            )
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "access_denied"

    def test_options_no_origin_returns_403(self, client):
        """OPTIONS preflight with no Origin header returns 403."""
        with patch("src.app_main.shared.core.cors.is_allowed", return_value=None):
            response = client.options("/cxtoken")
            assert response.status_code == 403


class TestCxtokenCorsOnIntegration:
    """Integration tests using real is_allowed behavior with CORS_ENABLED."""

    def test_get_same_origin_passes_real_cors(self, app, client):
        """GET from same origin passes real CORS check."""
        with patch(
            "src.app_main.public.routes.cxtoken.routes.get_user_token_by_username",
            return_value=None,
        ):
            response = client.get(
                "/cxtoken?wiki=en&user=UnknownUser",
                base_url=f"https://{ALLOWED_DOMAIN}",
                headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
            )
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "no access"

    def test_get_disallowed_origin_blocked_real_cors(self, app, client):
        """GET from disallowed origin is blocked by real CORS check."""
        response = client.get(
            "/cxtoken?wiki=en&user=TestUser",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": "https://evil.com"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"]["code"] == "access_denied"

    def test_options_same_origin_passes_real_cors(self, app, client):
        """OPTIONS from same origin passes real CORS check."""
        response = client.options(
            "/cxtoken",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers

    def test_options_from_allowed_cross_origin_passes_real_cors(self, app, client):
        """OPTIONS from allowed cross-origin domain passes real CORS check."""
        response = client.options(
            "/cxtoken",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": "https://mdwikicx.toolforge.org"},
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers
