"""
Tests for check_cors and validate_access on publish routes
with CORS_ENABLED (CORS_DISABLED=False).
"""

import json
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

    from src.new_app.public.routes.publish.routes import bp_publish

    app.register_blueprint(bp_publish)
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client."""
    return app.test_client()


class TestCheckCorsOnPublish:
    """Tests for @check_cors decorator on publish OPTIONS route with CORS_ENABLED."""

    def test_options_allowed_origin_returns_200(self, client):
        """OPTIONS preflight from allowed origin returns 200 with CORS headers."""
        with patch("src.new_app.shared.cors.is_allowed", return_value=ALLOWED_DOMAIN):
            response = client.options(
                "/publish/",
                headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
            )
            assert response.status_code == 200
            assert "Access-Control-Allow-Methods" in response.headers
            assert response.headers["Access-Control-Allow-Origin"] == f"https://{ALLOWED_DOMAIN}"

    def test_options_disallowed_origin_returns_403(self, client):
        """OPTIONS preflight from disallowed origin returns 403."""
        with patch("src.new_app.shared.cors.is_allowed", return_value=None):
            response = client.options(
                "/publish/",
                headers={"Origin": "https://evil.com"},
            )
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "access_denied"
            assert "authorized domains" in data["error"]["info"]

    def test_options_no_origin_returns_403(self, client):
        """OPTIONS preflight with no Origin returns 403."""
        with patch("src.new_app.shared.cors.is_allowed", return_value=None):
            response = client.options("/publish/")
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "access_denied"

    def test_options_same_origin_passes_cors(self, client):
        """OPTIONS from same origin (origin matches server host) passes CORS check."""
        with patch("src.new_app.shared.cors.is_allowed", return_value=ALLOWED_DOMAIN):
            response = client.options(
                "/publish/",
                base_url=f"https://{ALLOWED_DOMAIN}",
                headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
            )
            assert response.status_code == 200
            assert "Access-Control-Allow-Methods" in response.headers


class TestValidateAccessOnPublish:
    """Tests for @validate_access decorator on publish POST route with CORS_ENABLED."""

    def test_post_disallowed_origin_returns_403(self, client):
        """POST from disallowed origin without secret key returns 403."""
        with (
            patch("src.new_app.shared.cors.is_allowed", return_value=None),
            patch("src.new_app.shared.cors.check_publish_secret_code", return_value=None),
        ):
            response = client.post(
                "/publish/",
                data=json.dumps({"user": "TestUser", "title": "Test Page"}),
                content_type="application/json",
            )
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "access_denied"
            assert "Invalid or missing secret key" in data["error"]["info"]

    def test_post_allowed_origin_proceeds_past_cors(self, client):
        """POST from allowed origin passes CORS and reaches handler logic."""
        with (
            patch("src.new_app.shared.cors.is_allowed", return_value=ALLOWED_DOMAIN),
            patch(
                "src.new_app.public.routes.publish.routes.get_user_token_by_username",
                return_value=None,
            ),
            patch("src.new_app.public.routes.publish.worker.ReportsDB") as mock_reports_db,
        ):
            mock_reports_db.return_value = MagicMock()

            response = client.post(
                "/publish/",
                data=json.dumps(
                    {
                        "user": "UnknownUser",
                        "title": "Test Page",
                        "target": "en",
                        "sourcetitle": "Source",
                        "text": "Content",
                    }
                ),
                content_type="application/json",
            )
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "noaccess"
            assert response.headers.get("Access-Control-Allow-Origin") == f"https://{ALLOWED_DOMAIN}"

    def test_post_with_valid_secret_key_bypasses_cors(self, client):
        """POST with valid secret key bypasses CORS even from disallowed origin."""
        with (
            patch("src.new_app.shared.cors.is_allowed", return_value=None),
            patch("src.new_app.shared.cors.check_publish_secret_code", return_value="evil.com"),
            patch(
                "src.new_app.public.routes.publish.routes.get_user_token_by_username",
                return_value=None,
            ),
            patch("src.new_app.public.routes.publish.worker.ReportsDB") as mock_reports_db,
        ):
            mock_reports_db.return_value = MagicMock()

            response = client.post(
                "/publish/",
                headers={"X-Secret-Key": "test-secret"},
                data=json.dumps(
                    {
                        "user": "UnknownUser",
                        "title": "Test Page",
                        "target": "en",
                        "sourcetitle": "Source",
                        "text": "Content",
                    }
                ),
                content_type="application/json",
            )
            # CORS bypassed by secret key; 403 from handler because user not found
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "noaccess"

    def test_post_allowed_origin_with_invalid_secret_key(self, client):
        """POST from allowed origin succeeds even if secret key is invalid."""
        with (
            patch("src.new_app.shared.cors.is_allowed", return_value=ALLOWED_DOMAIN),
            patch("src.new_app.shared.cors.check_publish_secret_code", return_value=None),
            patch(
                "src.new_app.public.routes.publish.routes.get_user_token_by_username",
                return_value=None,
            ),
            patch("src.new_app.public.routes.publish.worker.ReportsDB") as mock_reports_db,
        ):
            mock_reports_db.return_value = MagicMock()

            response = client.post(
                "/publish/",
                data=json.dumps(
                    {
                        "user": "UnknownUser",
                        "title": "Test Page",
                        "target": "en",
                        "sourcetitle": "Source",
                        "text": "Content",
                    }
                ),
                content_type="application/json",
            )
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "noaccess"

    def test_post_disallowed_origin_and_no_secret_key(self, client):
        """POST from disallowed origin without secret key returns specific error info."""
        with (
            patch("src.new_app.shared.cors.is_allowed", return_value=None),
            patch("src.new_app.shared.cors.check_publish_secret_code", return_value=None),
        ):
            response = client.post(
                "/publish/",
                headers={"Origin": "https://evil.com"},
                data=json.dumps({"user": "TestUser", "title": "Test Page"}),
                content_type="application/json",
            )
            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "access_denied"
            assert "secret key" in data["error"]["info"]


class TestPublishCorsOnIntegration:
    """Integration tests using real is_allowed behavior with CORS_ENABLED."""

    def test_options_same_origin_passes_real_cors(self, app, client):
        """OPTIONS from same origin passes real CORS check."""
        response = client.options(
            "/publish/",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": f"https://{ALLOWED_DOMAIN}"},
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers

    def test_options_disallowed_origin_blocked_real_cors(self, app, client):
        """OPTIONS from disallowed origin is blocked by real CORS check."""
        response = client.options(
            "/publish/",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": "https://evil.com"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"]["code"] == "access_denied"

    def test_options_from_allowed_cross_origin_passes_real_cors(self, app, client):
        """OPTIONS from allowed cross-origin domain passes real CORS check."""
        response = client.options(
            "/publish/",
            base_url=f"https://{ALLOWED_DOMAIN}",
            headers={"Origin": "https://mdwikicx.toolforge.org"},
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers
