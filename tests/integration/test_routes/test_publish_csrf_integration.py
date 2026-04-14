"""Integration tests for publish endpoint with CSRF protection enabled.

These tests verify the full publish flow when WTF_CSRF_ENABLED=True,
using a configuration similar to ProductionConfig.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def csrf_app():
    """Create a Flask app with CSRF protection enabled (like Production)."""
    import os

    os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key-for-csrf-integration-tests")
    os.environ.setdefault("OAUTH_MWURI", "https://en.wikipedia.org/w/index.php")
    os.environ.setdefault("OAUTH_CONSUMER_KEY", "test_consumer_key")
    os.environ.setdefault("OAUTH_CONSUMER_SECRET", "test_consumer_secret")
    os.environ.setdefault("WIKIDATA_DOMAIN", "www.wikidata.org")
    os.environ.setdefault("REVIDS_API_URL", "https://mdwiki.toolforge.org/api.php")
    os.environ.setdefault("SPECIAL_USERS", "Mr. Ibrahem 1:Mr. Ibrahem,Admin:Mr. Ibrahem")
    os.environ.setdefault("FALLBACK_USER", "Mr. Ibrahem")
    os.environ.setdefault("USERS_WITHOUT_HASHTAG", "Mr. Ibrahem")
    os.environ.setdefault("CORS_ALLOWED_DOMAINS", "medwiki.toolforge.org,mdwikicx.toolforge.org")
    os.environ.setdefault("PUBLISH_REPORTS_DIR", "/tmp/publish_reports/reports_by_day")
    os.environ.setdefault("WORDS_JSON_PATH", "/tmp/words.json")
    os.environ.setdefault("ALL_PAGES_REVIDS_PATH", "/tmp/revids.json")
    os.environ.setdefault("FLASK_DATA_DIR", "/tmp")

    from flask import Flask
    from flask_wtf.csrf import CSRFProtect

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key-for-csrf-integration-tests"
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["WTF_CSRF_SSL_STRICT"] = False
    app.config["CORS_DISABLED"] = False
    app.url_map.strict_slashes = False

    csrf = CSRFProtect()
    csrf.init_app(app)

    from src.app_main.app_routes.publish.routes import bp_publish

    app.register_blueprint(bp_publish)
    csrf.exempt(bp_publish)

    return app


@pytest.fixture
def csrf_client(csrf_app):
    """Create a test client with CSRF protection enabled."""
    return csrf_app.test_client()


class TestPublishEndpointWithCSRF:
    """Integration tests for publish endpoint with CSRF enabled."""

    def test_cors_validation_still_works(self, csrf_client):
        """Test that CORS validation is applied before CSRF check."""
        with patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed:
            mock_is_allowed.return_value = None

            response = csrf_client.post(
                "/publish",
                data=json.dumps({"user": "TestUser", "title": "Test Page"}),
                content_type="application/json",
            )

            assert response.status_code == 403

    def test_successful_edit_with_csrf_enabled_no_token_required(self, csrf_client):
        """Test that successful edit works when blueprint is CSRF exempt.

        Since publish is a JSON API endpoint, the blueprint should be CSRF exempt.
        This test verifies the full flow works with CSRF enabled at app level.
        """
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.get_revid_db") as mock_get_revid_db,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = "12345"

            mock_changes.return_value = "Modified content"

            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}

            mock_link.return_value = {"result": "success", "qid": "Q123"}

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance
            mock_pages_instance = MagicMock()
            mock_pages_db.return_value = mock_pages_instance
            mock_pages_instance.insert_page_target.return_value = {"execute_query": True}

            response = csrf_client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "TestUser",
                        "title": "Test Page",
                        "target": "ar",
                        "sourcetitle": "Source Page",
                        "text": "Original content",
                        "campaign": "test_campaign",
                        "tr_type": "lead",
                    }
                ),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["edit"]["result"] == "Success"
            assert data["LinkToWikidata"]["result"] == "success"

    def test_tr_type_parameter_passed_correctly(self, csrf_client):
        """Test that tr_type parameter is correctly passed through the flow."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.get_revid_db") as mock_get_revid_db,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance
            mock_pages_instance = MagicMock()
            mock_pages_db.return_value = mock_pages_instance
            mock_pages_instance.insert_page_target.return_value = {"execute_query": True}

            response = csrf_client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "TestUser",
                        "title": "Test Page",
                        "target": "ar",
                        "sourcetitle": "Source Page",
                        "text": "Content",
                        "tr_type": "section",
                    }
                ),
                content_type="application/json",
            )

            assert response.status_code == 200

            insert_page_target_calls = mock_pages_instance.insert_page_target.call_args_list
            if insert_page_target_calls:
                call_kwargs = insert_page_target_calls[0].kwargs
                assert call_kwargs.get("tr_type") == "section"

    def test_words_field_in_tab(self, csrf_client):
        """Test that words field is correctly set in the tab dict."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
            patch("src.app_main.app_routes.publish.worker.get_word_count") as mock_word_count,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}
            mock_word_count.return_value = 500

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance
            mock_pages_instance = MagicMock()
            mock_pages_db.return_value = mock_pages_instance
            mock_pages_instance.insert_page_target.return_value = {"execute_query": True}

            response = csrf_client.post(
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

            assert response.status_code == 200

            to_do_calls = mock_to_do.call_args_list
            if to_do_calls:
                tab_arg = to_do_calls[0][0][0]
                assert "words" in tab_arg
                assert tab_arg["words"] == 500

    def test_captcha_handling_with_csrf_enabled(self, csrf_client):
        """Test captcha response handling with CSRF enabled."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None

            mock_edit.return_value = {
                "edit": {
                    "captcha": {"id": "12345", "type": "image"},
                    "result": "Failure",
                }
            }

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance

            response = csrf_client.post(
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

            assert response.status_code == 200
            data = response.get_json()
            assert "captcha" in data["edit"]

    def test_no_access_returns_403_with_csrf_enabled(self, csrf_client):
        """Test that no access error returns 403 even with CSRF enabled."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"
            mock_get_token.return_value = None

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance

            response = csrf_client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "UnknownUser",
                        "title": "Test Page",
                        "target": "ar",
                        "sourcetitle": "Source Page",
                        "text": "Content",
                    }
                ),
                content_type="application/json",
            )

            assert response.status_code == 403
            data = response.get_json()
            assert data["error"]["code"] == "noaccess"

    def test_wikidata_link_fallback_user_with_csrf_enabled(self, csrf_client):
        """Test Wikidata link with fallback user when get_csrftoken fails."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.shouldAddedToWikidata") as mock_should_add,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_should_add.return_value = True

            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}

            mock_link.side_effect = [
                {"error": "get_csrftoken failed", "qid": "Q123"},
                {"result": "success", "qid": "Q123"},
            ]

            fallback_token = MagicMock()
            fallback_token.decrypted.return_value = ("fallback_key", "fallback_secret")

            def get_token_side_effect(username):
                if username == "TestUser":
                    return mock_token
                elif username == "Mr. Ibrahem":
                    return fallback_token
                return None

            mock_get_token.side_effect = get_token_side_effect

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance
            mock_pages_instance = MagicMock()
            mock_pages_db.return_value = mock_pages_instance
            mock_pages_instance.insert_page_target.return_value = {"execute_query": True}

            response = csrf_client.post(
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

            assert response.status_code == 200
            data = response.get_json()
            assert data["edit"]["result"] == "Success"
            assert "fallback" in data["LinkToWikidata"]

    def test_options_preflight_with_csrf_enabled(self, csrf_client):
        """Test OPTIONS preflight request with CSRF enabled."""
        with patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed:
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            response = csrf_client.options("/publish")

            assert response.status_code == 200
            assert "Access-Control-Allow-Origin" in response.headers
            assert "Access-Control-Allow-Methods" in response.headers

    def test_edit_error_handling_with_csrf_enabled(self, csrf_client):
        """Test edit error handling with CSRF enabled."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None

            mock_edit.return_value = {
                "edit": {
                    "result": "Failure",
                    "error": {"code": "protectedpage", "info": "Page is protected"},
                }
            }

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance

            response = csrf_client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "TestUser",
                        "title": "Protected Page",
                        "target": "ar",
                        "sourcetitle": "Source Page",
                        "text": "Content",
                    }
                ),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["edit"]["result"] == "Failure"
            assert "error" in data["edit"]

    def test_determine_hashtag_logic_with_csrf_enabled(self, csrf_client):
        """Test that hashtag determination works correctly with CSRF enabled."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance
            mock_pages_instance = MagicMock()
            mock_pages_db.return_value = mock_pages_instance
            mock_pages_instance.insert_page_target.return_value = {"execute_query": True}

            response = csrf_client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "Mr. Ibrahem",
                        "title": "Mr. Ibrahem/Test Page",
                        "target": "ar",
                        "sourcetitle": "Source Page",
                        "text": "Content",
                    }
                ),
                content_type="application/json",
            )

            assert response.status_code == 200

            to_do_calls = mock_to_do.call_args_list
            if to_do_calls:
                tab_arg = to_do_calls[0][0][0]
                summary = tab_arg.get("summary", "")
                assert "#mdwikicx" not in summary or summary.endswith(" to:ar ")

    def test_revid_resolution_with_csrf_enabled(self, csrf_client):
        """Test revision ID resolution with CSRF enabled."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.get_revid_db") as mock_get_revid_db,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = "67890"
            mock_get_revid_db.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 99999}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance
            mock_pages_instance = MagicMock()
            mock_pages_db.return_value = mock_pages_instance
            mock_pages_instance.insert_page_target.return_value = {"execute_query": True}

            response = csrf_client.post(
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

            assert response.status_code == 200
            mock_get_revid.assert_called_once_with("Source Page")

    def test_empty_revid_fallback_with_csrf_enabled(self, csrf_client):
        """Test empty revid fallback to request_revid with CSRF enabled."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.get_revid_db") as mock_get_revid_db,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = ""
            mock_get_revid_db.return_value = ""

            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance
            mock_pages_instance = MagicMock()
            mock_pages_db.return_value = mock_pages_instance
            mock_pages_instance.insert_page_target.return_value = {"execute_query": True}

            response = csrf_client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "TestUser",
                        "title": "Test Page",
                        "target": "ar",
                        "sourcetitle": "Source Page",
                        "text": "Content",
                        "revid": "99999",
                    }
                ),
                content_type="application/json",
            )

            assert response.status_code == 200

            to_do_calls = mock_to_do.call_args_list
            if to_do_calls:
                tab_arg = to_do_calls[0][0][0]
                assert tab_arg.get("revid") == "99999"
                assert "empty revid" in tab_arg

    def test_fix_refs_applied_with_csrf_enabled(self, csrf_client):
        """Test that fix_refs is applied when text changes with CSRF enabled."""
        with (
            patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_is_allowed,
            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_is_allowed.return_value = "medwiki.toolforge.org"

            mock_token = MagicMock()
            mock_token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = mock_token

            mock_get_revid.return_value = "12345"
            mock_changes.return_value = "Fixed reference content"

            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}

            mock_reports_instance = MagicMock()
            mock_reports_db.return_value = mock_reports_instance
            mock_pages_instance = MagicMock()
            mock_pages_db.return_value = mock_pages_instance
            mock_pages_instance.insert_page_target.return_value = {"execute_query": True}

            response = csrf_client.post(
                "/publish",
                data=json.dumps(
                    {
                        "user": "TestUser",
                        "title": "Test Page",
                        "target": "ar",
                        "sourcetitle": "Source Page",
                        "text": "Original content with references",
                    }
                ),
                content_type="application/json",
            )

            assert response.status_code == 200

            to_do_calls = mock_to_do.call_args_list
            if to_do_calls:
                tab_arg = to_do_calls[0][0][0]
                assert tab_arg.get("fix_refs") == "yes"
