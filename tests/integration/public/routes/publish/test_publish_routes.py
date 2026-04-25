"""
Integration tests for src/sqlalchemy_app/public/routes/publish/routes.py module.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient


@pytest.mark.integration
class TestPublishPreflight:
    """Integration tests for the publish preflight endpoint."""

    def test_preflight_returns_200(self, client: FlaskClient):
        """Test that OPTIONS request returns 200."""
        response = client.options("/publish/")

        assert response.status_code == 200

    def test_preflight_sets_cors_headers(self, client: FlaskClient):
        """Test that preflight sets correct CORS headers."""
        response = client.options("/publish/")

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers


@pytest.mark.integration
class TestPublishPost:
    """Integration tests for the publish POST endpoint."""

    def test_publish_requires_post_method(self, client: FlaskClient):
        """Test that GET request to publish endpoint is not allowed."""
        response = client.get("/publish/")

        # Should return 405 Method Not Allowed
        assert response.status_code == 405

    def test_publish_no_data_returns_error(self, client: FlaskClient):
        """Test that empty request data returns error."""
        with patch("src.sqlalchemy_app.public.routes.publish.routes.validate_access") as mock_validate:
            mock_validate.return_value = lambda f: f

            response = client.post("/publish/", data={})

            # Should handle empty data gracefully
            assert response.status_code == 400

    def test_publish_missing_user_token_returns_403(self, client: FlaskClient):
        """Test that missing user token returns 403."""
        with patch("src.sqlalchemy_app.public.routes.publish.routes.validate_access") as mock_validate:
            mock_validate.return_value = lambda f: f

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

    def test_publish_with_valid_data(self, client: FlaskClient):
        """Test publishing with valid data."""
        with patch("src.sqlalchemy_app.public.routes.publish.routes.validate_access") as mock_validate:
            mock_validate.return_value = lambda f: f

            mock_user_token = MagicMock()
            mock_user_token.decrypted.return_value = ("access_key", "access_secret")

            with patch("src.sqlalchemy_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token:
                mock_get_token.return_value = mock_user_token

                with patch("src.sqlalchemy_app.public.routes.publish.routes._process_edit") as mock_process:
                    mock_process.return_value = {"result": "success", "edit": {"newrevid": 12345}}

                    response = client.post(
                        "/publish/",
                        data={
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

    def test_publish_accepts_form_data(self, client: FlaskClient):
        """Test that publish accepts form data."""
        with patch("src.sqlalchemy_app.public.routes.publish.routes.validate_access") as mock_validate:
            mock_validate.return_value = lambda f: f

            mock_user_token = MagicMock()
            mock_user_token.decrypted.return_value = ("access_key", "access_secret")

            with patch("src.sqlalchemy_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token:
                mock_get_token.return_value = mock_user_token

                with patch("src.sqlalchemy_app.public.routes.publish.routes._process_edit") as mock_process:
                    mock_process.return_value = {"result": "success"}

                    response = client.post(
                        "/publish/",
                        data={
                            "user": "TestUser",
                            "title": "Test_Page",
                            "target": "en",
                            "text": "Test content",
                        },
                    )

                    assert response.status_code == 200

    def test_publish_accepts_json_data(self, client: FlaskClient):
        """Test that publish accepts JSON data."""
        with patch("src.sqlalchemy_app.public.routes.publish.routes.validate_access") as mock_validate:
            mock_validate.return_value = lambda f: f

            mock_user_token = MagicMock()
            mock_user_token.decrypted.return_value = ("access_key", "access_secret")

            with patch("src.sqlalchemy_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token:
                mock_get_token.return_value = mock_user_token

                with patch("src.sqlalchemy_app.public.routes.publish.routes._process_edit") as mock_process:
                    mock_process.return_value = {"result": "success"}

                    response = client.post(
                        "/publish/",
                        json={
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

    def test_publish_with_captcha_params(self, client: FlaskClient):
        """Test publishing with captcha parameters."""
        with patch("src.sqlalchemy_app.public.routes.publish.routes.validate_access") as mock_validate:
            mock_validate.return_value = lambda f: f

            mock_user_token = MagicMock()
            mock_user_token.decrypted.return_value = ("access_key", "access_secret")

            with patch("src.sqlalchemy_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token:
                mock_get_token.return_value = mock_user_token

                with patch("src.sqlalchemy_app.public.routes.publish.routes._process_edit") as mock_process:
                    mock_process.return_value = {"result": "success"}

                    response = client.post(
                        "/publish/",
                        data={
                            "user": "TestUser",
                            "title": "Test Page",
                            "target": "en",
                            "text": "Test content",
                            "wpCaptchaId": "123",
                            "wpCaptchaWord": "answer",
                        },
                    )

                    assert response.status_code == 200
