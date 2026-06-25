"""Tests for app_routes.post module."""

import json
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.main_app import create_app
from src.main_app.config import TestingConfig


@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    import os

    os.environ.setdefault("CORS_ALLOWED_DOMAINS", "")

    _app = create_app(TestingConfig)
    _app.config.update({"CORS_DISABLED": True})

    return _app


@pytest.fixture
def client(app: Flask, setup_db) -> FlaskClient:
    """Create a test client."""
    return app.test_client()


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
        with (
            patch("src.main_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.main_app.public.routes.publish.worker.to_do") as mock_to_do,
            patch("src.main_app.public.routes.publish.worker.add_report") as mock_load_reports_db,
        ):
            mock_get_token.return_value = None
            mock_load_reports_db.return_value = None

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

    def test_successful_edit_returns_success(self, client):
        """Test that successful edit returns success result."""
        with (
            patch("src.main_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.main_app.public.routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.main_app.public.routes.publish.worker.get_revid_db") as mock_get_revid_db,
            patch("src.main_app.public.routes.publish.worker.do_changes_to_text_with_settings") as mock_changes,
            patch("src.main_app.public.routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.main_app.public.routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.main_app.public.routes.publish.worker.to_do") as mock_to_do,
            patch("src.main_app.public.routes.publish.worker.add_report") as mock_load_reports_db,
            patch("src.main_app.public.routes.publish.worker.shouldAddedToWikidata") as mock_should_add,
            patch("src.main_app.public.routes.publish.to_db.find_exists_or_update_page") as mock_find_exists,
            patch("src.main_app.public.routes.publish.to_db.insert_page_target") as mock_insert_page,
            patch("src.main_app.public.routes.publish.to_db.get_campaign_category") as mock_get_campaign_category,
        ):
            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token
            mock_should_add.return_value = True

            # Mock revision ID
            mock_get_revid.return_value = "12345"

            # Mock text changes
            mock_changes.return_value = "Modified content"

            # Mock successful edit
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}

            # Mock Wikidata link
            mock_link.return_value = {"result": "success", "qid": "Q123"}

            mock_load_reports_db.return_value = None

            response = client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "TestUser",
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

    def test_handles_captcha_response(self, client):
        """Test that captcha response is handled correctly."""
        with (
            patch("src.main_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.main_app.public.routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.main_app.public.routes.publish.worker.do_changes_to_text_with_settings") as mock_changes,
            patch("src.main_app.public.routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.main_app.public.routes.publish.worker.to_do") as mock_to_do,
            patch("src.main_app.public.routes.publish.worker.add_report") as mock_load_reports_db,
        ):
            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            # Mock revision ID
            mock_get_revid.return_value = "12345"

            # Mock text changes
            mock_changes.return_value = None

            # Mock captcha response
            mock_edit.return_value = {"edit": {"captcha": {"id": "123", "type": "image"}}}

            mock_load_reports_db.return_value = None

            response = client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "TestUser",
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
