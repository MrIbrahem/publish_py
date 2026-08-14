"""Tests for app_routes.post module."""

import json
import os
from unittest.mock import patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.main_app import AppFactory
from src.main_app.config import TestingConfig
from src.main_app.database.services import UsersService, UserTokenService
from src.main_app.services.core.crypto import CryptoService


@pytest.fixture
def mock_app() -> Flask:
    """Create a test Flask application."""

    os.environ.setdefault("CORS_ALLOWED_DOMAINS", "")

    _app = AppFactory.create(TestingConfig)
    _app.config.update({"CORS_DISABLED": True})

    return _app


@pytest.fixture
def client(mock_app: Flask, setup_db) -> FlaskClient:
    """Create a test client."""
    return mock_app.test_client()


@pytest.fixture
def real_user_token():
    """Create a real user and token in the database for publish tests."""
    users_service = UsersService()
    user = users_service.create_user("PublishUser")

    token_service = UserTokenService()
    encrypted_token = CryptoService().encrypt("test_access_token")
    encrypted_secret = CryptoService().encrypt("test_access_secret")
    token_service.create(
        user_id=user.user_id,
        access_token=encrypted_token,
        access_secret=encrypted_secret,
    )
    return user


class TestPostEndpoint:
    """Tests for post endpoint."""

    @pytest.mark.skip(reason="Test client uses localhost which triggers same-origin bypass in CORS check")
    def test_cors_not_allowed_without_origin(self, client):
        """Test that requests from unauthorized origins are rejected when no secret key is provided."""
        response = client.post(
            "/publish",
            base_url="https://medwiki.toolforge.org",
            headers={"Origin": "https://attacker-site.com"},
            data=json.dumps({"user": "TestUser", "title": "Test Page"}),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_no_access_returns_when_user_not_found(self, client):
        """Test that no access error is returned when user not found."""
        response = client.post(
            "/publish",
            data=json.dumps(
                {
                    "user": "UnknownUser",
                    "title": "Test Page",
                    "target": "en",
                    "sourcetitle": "Source Page",
                    "text": "Content",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 403
        data = response.get_json()
        assert isinstance(data, dict)

        assert "error" in data
        assert isinstance(data["error"], dict)
        assert data["error"]["code"] == "noaccess"

    def test_handles_options_request(self, client):
        """Test that OPTIONS request is handled for CORS preflight."""
        response = client.options(
            "/publish",
            base_url="https://medwiki.toolforge.org",
            headers={"Origin": "https://medwiki.toolforge.org"},
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers

    def test_successful_edit_returns_success(self, real_user_token, client):
        """Test that successful edit returns success result."""
        with (
            patch("src.main_app.public.routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.main_app.public.routes.publish.worker.get_revid_db"),
            patch("src.main_app.public.routes.publish.worker.do_changes_to_text_with_settings") as mock_changes,
            patch("src.main_app.public.routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.main_app.public.routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.main_app.public.routes.publish.worker.to_do"),
            patch("src.main_app.public.routes.publish.worker.should_added_to_wikidata") as mock_should_add,
            patch("src.main_app.public.routes.publish.to_db.find_exists_or_update_page"),
            patch("src.main_app.public.routes.publish.to_db.CategoryService.get_campaign_category"),
        ):
            mock_should_add.return_value = True
            mock_get_revid.return_value = "12345"
            mock_changes.return_value = "Modified content"
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}

            response = client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "PublishUser",
                        "title": "Test Page",
                        "target": "ar",
                        "sourcetitle": "Source Page",
                        "text": "Original content",
                    }
                ),
                content_type="application/json",
            )
            assert response.status_code == 200

            data = response.get_json()
            assert data["edit"]["result"] == "Success"

    def test_handles_captcha_response(self, real_user_token, client):
        """Test that captcha response is handled correctly."""
        with (
            patch("src.main_app.public.routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.main_app.public.routes.publish.worker.do_changes_to_text_with_settings") as mock_changes,
            patch("src.main_app.public.routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.main_app.public.routes.publish.worker.to_do"),
        ):
            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"captcha": {"id": "123", "type": "image"}}}

            response = client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "PublishUser",
                        "title": "Test Page",
                        "target": "ar",
                        "sourcetitle": "Source Page",
                        "text": "Content",
                    }
                ),
                content_type="application/json",
            )

            data = response.get_json()
            assert "captcha" in data["edit"]
