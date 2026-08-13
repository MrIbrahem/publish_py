"""
Integration tests for src/main_app/public/routes/publish/routes.py module.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from flask.testing import FlaskClient

from src.main_app.database.services import UsersService, UserTokenService


@pytest.fixture
def mock_validate_access():
    """Bypass CORS/secret checks performed by `validate_access` at request time."""
    with (
        patch("src.main_app.shared.core.cors.is_allowed", return_value="https://example.com"),
        patch("src.main_app.shared.core.cors.check_publish_secret_code", return_value=True),
    ):
        yield


@pytest.fixture
def real_user_token():
    """Create a real user and token in the database for publish tests."""
    users_service = UsersService()
    user = users_service.create_user("PublishUser")

    token_service = UserTokenService()
    encrypted_token = token_service.encrypt_value("test_access_token")
    encrypted_secret = token_service.encrypt_value("test_access_secret")
    token_service.create_user_token(user.user_id, encrypted_token, encrypted_secret)
    return user


@pytest.mark.integration
class TestPublishPreflight:
    """Integration tests for the publish preflight endpoint."""

    def test_preflight_returns_200(self, mock_validate_access, mock_client: FlaskClient):
        """Test that OPTIONS request returns 200."""
        response = mock_client.options("/publish/")

        assert response.status_code == 200

    def test_preflight_sets_cors_headers(self, mock_validate_access, mock_client: FlaskClient):
        """Test that preflight sets correct CORS headers."""
        response = mock_client.options("/publish/")

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers


@pytest.mark.integration
class TestPublishPost:
    """Integration tests for the publish POST endpoint."""

    def test_publish_requires_post_method(self, mock_validate_access, mock_client: FlaskClient):
        """Test that GET request to publish endpoint is not allowed."""
        response = mock_client.get("/publish/")

        # Should return 405 Method Not Allowed
        assert response.status_code == 405

    def test_publish_no_data_returns_error(self, mock_validate_access, mock_client: FlaskClient):
        """Test that empty request data returns error."""

        response = mock_client.post("/publish/", data={})

        # Should handle empty data gracefully
        assert response.status_code == 400

    def test_publish_missing_user_token_returns_403(self, mock_validate_access, mock_client: FlaskClient):
        """Test that missing user token returns 403."""
        response = mock_client.post(
            "/publish/",
            data={
                "translate_type": "lead",
                "user": "NonExistentUser",
                "title": "Test Page",
                "target": "en",
                "text": "Test content",
            },
        )

        data = response.get_json()
        assert "error" in data
        assert response.status_code == 403

    def test_publish_with_valid_data(self, real_user_token, mock_validate_access, mock_client: FlaskClient):
        """Test publishing with valid data."""
        with patch("src.main_app.public.routes.publish.routes._process_edit") as mock_process:
            mock_process.return_value = {"result": "success", "edit": {"newrevid": 12345}}

            response = mock_client.post(
                "/publish/",
                data={
                    "translate_type": "lead",
                    "user": "PublishUser",
                    "title": "Test Page",
                    "target": "en",
                    "text": "Test content",
                    "sourcetitle": "Source Page",
                },
            )

            data = response.get_json()
            assert "result" in data
            assert response.status_code == 200


@pytest.mark.integration
class TestPublishFormData:
    """Integration tests for publish form data handling."""

    def test_publish_accepts_form_data(self, real_user_token, mock_validate_access, mock_client: FlaskClient):
        """Test that publish accepts form data."""
        with patch("src.main_app.public.routes.publish.routes._process_edit") as mock_process:
            mock_process.return_value = {"result": "success"}

            response = mock_client.post(
                "/publish/",
                data={
                    "translate_type": "lead",
                    "user": "PublishUser",
                    "title": "Test_Page",
                    "target": "en",
                    "text": "Test content",
                },
            )

            assert response.status_code == 200

    def test_publish_accepts_json_data(self, real_user_token, mock_validate_access, mock_client: FlaskClient):
        """Test that publish accepts JSON data."""
        with patch("src.main_app.public.routes.publish.routes._process_edit") as mock_process:
            mock_process.return_value = {"result": "success"}

            response = mock_client.post(
                "/publish/",
                json={
                    "translate_type": "lead",
                    "user": "PublishUser",
                    "title": "Test Page",
                    "target": "en",
                    "text": "Test content",
                },
                content_type="application/json",
            )

            assert response.status_code == 200


@pytest.mark.integration
class TestPublishCaptcha:
    """Integration tests for captcha handling in publish."""

    def test_publish_with_captcha_params(self, real_user_token, mock_validate_access, mock_client: FlaskClient):
        """Test publishing with captcha parameters."""
        with patch("src.main_app.public.routes.publish.routes._process_edit") as mock_process:
            mock_process.return_value = {"result": "success"}

            response = mock_client.post(
                "/publish/",
                data={
                    "translate_type": "lead",
                    "user": "PublishUser",
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

    def test_publish_requires_post_method(self, mock_validate_access, mock_client):
        """Test that publish route requires POST method."""
        response = mock_client.get("/publish")

        # Should return 404 (not found) or 405 (method not allowed)
        assert response.status_code == 404
