"""
Integration tests for src/sqlalchemy_app/public/routes/publish/routes.py module.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.fixture
def mock_validate_access() -> MagicMock:
    """Mock the validate_access function."""
    with patch("src.sqlalchemy_app.public.routes.publish.routes.validate_access") as mock_validate:
        mock_validate.return_value = lambda f: f


@pytest.fixture
def mock_user_token() -> MagicMock:

    _mock = MagicMock()
    _mock.decrypted.return_value = ("access_key", "access_secret")

    with patch("src.sqlalchemy_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token:
        mock_get_token.return_value = _mock


@pytest.mark.integration
class TestPublishPreflight:
    """Integration tests for the publish preflight endpoint."""

    def test_preflight_returns_200(self, mock_validate_access, client: FlaskClient):
        """Test that OPTIONS request returns 200."""
        response = client.options("/publish/")

        assert response.status_code == 200

    def test_preflight_sets_cors_headers(self, mock_validate_access, client: FlaskClient):
        """Test that preflight sets correct CORS headers."""
        response = client.options("/publish/")

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers


@pytest.mark.integration
class TestPublishPost:
    """Integration tests for the publish POST endpoint."""

    def test_publish_requires_post_method(self, mock_validate_access, client: FlaskClient):
        """Test that GET request to publish endpoint is not allowed."""
        response = client.get("/publish/")

        # Should return 405 Method Not Allowed
        assert response.status_code == 405

    def test_publish_no_data_returns_error(self, mock_validate_access, client: FlaskClient):
        """Test that empty request data returns error."""

        response = client.post("/publish/", data={})

        # Should handle empty data gracefully
        assert response.status_code == 400

    def test_publish_missing_user_token_returns_403(self, mock_validate_access, client: FlaskClient):
        """Test that missing user token returns 403."""

        with patch("src.sqlalchemy_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token:
            mock_get_token.return_value = None

            response = client.post(
                "/publish/",
                data={
                    "user": "TestUser",
                    "title": "Test Page",
                    "target": "en",
                    "text": "Test content",
                },
            )

            assert response.status_code == 403
            data = response.get_json()
            assert "error" in data

    def test_publish_with_valid_data(self, mock_user_token, mock_validate_access, client: FlaskClient):
        """Test publishing with valid data."""

        with patch("src.sqlalchemy_app.public.routes.publish.routes._process_edit") as mock_process:
            mock_process.return_value = {"result": "success", "edit": {"newrevid": 12345}}

            response = client.post(
                "/publish/",
                data={
                    "translate_type": "lead",
                    "user": "TestUser",
                    "title": "Test Page",
                    "target": "en",
                    "text": "Test content",
                    "sourcetitle": "Source Page",
                },
            )

            assert response.status_code == 200
            data = response.get_json()
            assert "result" in data


@pytest.mark.integration
class TestPublishFormData:
    """Integration tests for publish form data handling."""

    def test_publish_accepts_form_data(self, mock_user_token, mock_validate_access, client: FlaskClient):
        """Test that publish accepts form data."""

        with patch("src.sqlalchemy_app.public.routes.publish.routes._process_edit") as mock_process:
            mock_process.return_value = {"result": "success"}

            response = client.post(
                "/publish/",
                data={
                    "translate_type": "lead",
                    "user": "TestUser",
                    "title": "Test_Page",
                    "target": "en",
                    "text": "Test content",
                },
            )

            assert response.status_code == 200

    def test_publish_accepts_json_data(self, mock_user_token, mock_validate_access, client: FlaskClient):
        """Test that publish accepts JSON data."""

        with patch("src.sqlalchemy_app.public.routes.publish.routes._process_edit") as mock_process:
            mock_process.return_value = {"result": "success"}

            response = client.post(
                "/publish/",
                json={
                    "translate_type": "lead",
                    "user": "TestUser",
                    "title": "Test Page",
                    "target": "en",
                    "text": "Test content",
                },
                content_type="application/json",
            )

            # May accept or reject JSON
            assert response.status_code == 200  # in [200, 400]


@pytest.mark.integration
class TestPublishCaptcha:
    """Integration tests for captcha handling in publish."""

    def test_publish_with_captcha_params(self, mock_user_token, mock_validate_access, client: FlaskClient):
        """Test publishing with captcha parameters."""

        with patch("src.sqlalchemy_app.public.routes.publish.routes._process_edit") as mock_process:
            mock_process.return_value = {"result": "success"}

            response = client.post(
                "/publish/",
                data={
                    "translate_type": "lead",
                    "user": "TestUser",
                    "title": "Test Page",
                    "target": "en",
                    "text": "Test content",
                    "wpCaptchaId": "123",
                    "wpCaptchaWord": "answer",
                },
            )

            assert response.status_code == 200


class TestPublishRouteIntegration:
    """Integration tests for publish route."""

    def test_publish_requires_post_method(self, mock_validate_access, client):
        """Test that publish route requires POST method."""
        response = client.get("/publish")

        # Should return 404 (not found) or 405 (method not allowed)
        assert response.status_code == 404

    def test_publish_rejects_missing_csrf(self, mock_validate_access, app):
        """Test that publish route rejects requests without CSRF token when enabled."""
        from src.sqlalchemy_app import create_app
        from src.sqlalchemy_app.config import Config

        class TestConfigWithCSRF(Config):
            WTF_CSRF_ENABLED = True

        test_app = create_app(TestConfigWithCSRF)
        test_client = test_app.test_client()

        response = test_client.post("/publish", data={"title": "Test"})

        # Route may return 404 if not registered, 400 for missing CSRF, or 302/403 for auth issues
        assert response.status_code == 403
