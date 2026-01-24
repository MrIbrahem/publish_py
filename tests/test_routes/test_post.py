"""Tests for app_routes.post module."""

import json
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask


@pytest.fixture
def app():
    """Create a test Flask application."""
    # Environment variables are set in conftest.py
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test_secret"

    # Import and register the blueprint
    from src.app.app_routes.post.routes import bp_post

    app.register_blueprint(bp_post)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestPostEndpoint:
    """Tests for post endpoint."""

    def test_cors_not_allowed_without_origin(self, client):
        """Test that requests without allowed origin are rejected."""
        with patch("src.app.app_routes.post.routes.is_allowed") as mock_is_allowed:
            mock_is_allowed.return_value = None

            response = client.post(
                "/",
                data=json.dumps({"user": "TestUser", "title": "Test Page"}),
                content_type="application/json",
            )

            assert response.status_code == 403
            assert b"Access denied" in response.data

    def test_returns_no_access_when_user_not_found(self, client):
        """Test that no access error is returned when user not found."""
        with patch("src.app.app_routes.post.routes.is_allowed") as mock_is_allowed, \
             patch("src.app.app_routes.post.routes.get_user_token_by_username") as mock_get_token, \
             patch("src.app.app_routes.post.routes.to_do") as mock_to_do, \
             patch("src.app.app_routes.post.routes.ReportsDB") as mock_reports_db:
            mock_is_allowed.return_value = "medwiki.toolforge.org"
            mock_get_token.return_value = None

            # Mock database
            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance

            response = client.post(
                "/",
                data=json.dumps({
                    "user": "UnknownUser",
                    "title": "Test Page",
                    "target": "en",
                    "sourcetitle": "Source Page",
                    "text": "Content",
                }),
                content_type="application/json",
            )

            assert response.status_code == 403
            data = response.get_json()
            assert "error" in data
            assert data["error"]["code"] == "noaccess"

    def test_handles_options_request(self, client):
        """Test that OPTIONS request is handled for CORS preflight."""
        with patch("src.app.app_routes.post.routes.is_allowed") as mock_is_allowed:
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            response = client.options("/")

            assert response.status_code == 200
            assert "Access-Control-Allow-Origin" in response.headers

    def test_successful_edit_returns_success(self, client):
        """Test that successful edit returns success result."""
        with patch("src.app.app_routes.post.routes.is_allowed") as mock_is_allowed, \
             patch("src.app.app_routes.post.routes.get_user_token_by_username") as mock_get_token, \
             patch("src.app.app_routes.post.routes.get_revid") as mock_get_revid, \
             patch("src.app.app_routes.post.routes.get_revid_db") as mock_get_revid_db, \
             patch("src.app.app_routes.post.routes.do_changes_to_text") as mock_changes, \
             patch("src.app.app_routes.post.routes.publish_do_edit") as mock_edit, \
             patch("src.app.app_routes.post.routes.link_to_wikidata") as mock_link, \
             patch("src.app.app_routes.post.routes.to_do") as mock_to_do, \
             patch("src.app.app_routes.post.routes.ReportsDB") as mock_reports_db, \
             patch("src.app.app_routes.post.routes.PagesDB") as mock_pages_db:

            mock_is_allowed.return_value = "medwiki.toolforge.org"

            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            # Mock revision ID
            mock_get_revid.return_value = "12345"

            # Mock text changes
            mock_changes.return_value = "Modified content"

            # Mock successful edit
            mock_edit.return_value = {
                "edit": {"result": "Success", "newrevid": 67890}
            }

            # Mock Wikidata link
            mock_link.return_value = {"result": "success", "qid": "Q123"}

            # Mock database operations
            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance
            mock_pages_instance = MagicMock()
            mock_pages_db.return_value = mock_pages_instance
            mock_pages_instance.insert_page_target.return_value = {"execute_query": True}

            response = client.post(
                "/",
                data=json.dumps({
                    "user": "TestUser",
                    "title": "Test Page",
                    "target": "ar",
                    "sourcetitle": "Source Page",
                    "text": "Original content",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["edit"]["result"] == "Success"

    def test_handles_captcha_response(self, client):
        """Test that captcha response is handled correctly."""
        with patch("src.app.app_routes.post.routes.is_allowed") as mock_is_allowed, \
             patch("src.app.app_routes.post.routes.get_user_token_by_username") as mock_get_token, \
             patch("src.app.app_routes.post.routes.get_revid") as mock_get_revid, \
             patch("src.app.app_routes.post.routes.do_changes_to_text") as mock_changes, \
             patch("src.app.app_routes.post.routes.publish_do_edit") as mock_edit, \
             patch("src.app.app_routes.post.routes.to_do") as mock_to_do, \
             patch("src.app.app_routes.post.routes.ReportsDB") as mock_reports_db:

            mock_is_allowed.return_value = "medwiki.toolforge.org"

            # Mock user token
            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            # Mock revision ID
            mock_get_revid.return_value = "12345"

            # Mock text changes
            mock_changes.return_value = None

            # Mock captcha response
            mock_edit.return_value = {
                "edit": {
                    "captcha": {"id": "123", "type": "image"}
                }
            }

            # Mock database
            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance

            response = client.post(
                "/",
                data=json.dumps({
                    "user": "TestUser",
                    "title": "Test Page",
                    "target": "ar",
                    "sourcetitle": "Source Page",
                    "text": "Content",
                }),
                content_type="application/json",
            )

            data = response.get_json()
            assert "captcha" in data["edit"]


class TestGetErrorsFile:
    """Tests for _get_errors_file function."""

    def test_returns_placeholder_for_unknown_error(self):
        """Test that placeholder is returned for unknown errors."""
        from src.app.app_routes.post.routes import _get_errors_file

        result = _get_errors_file({"some": "error"}, "errors")

        assert result == "errors"

    def test_returns_protectedpage_for_protected_error(self):
        """Test that protectedpage is returned for protected page error."""
        from src.app.app_routes.post.routes import _get_errors_file

        result = _get_errors_file({"error": {"code": "protectedpage"}}, "errors")

        assert result == "protectedpage"

    def test_returns_ratelimited_for_rate_limit_error(self):
        """Test that ratelimited is returned for rate limit error."""
        from src.app.app_routes.post.routes import _get_errors_file

        result = _get_errors_file({"error": {"info": "ratelimited"}}, "errors")

        assert result == "ratelimited"
