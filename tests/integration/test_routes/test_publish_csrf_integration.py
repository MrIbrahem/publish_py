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
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-for-csrf-integration-tests",
        "WTF_CSRF_ENABLED": True,
        "WTF_CSRF_SSL_STRICT": False,
        "CORS_DISABLED": False,
    })
    app.url_map.strict_slashes = False

    csrf = CSRFProtect(app)
    from src.app_main.app_routes.publish.routes import bp_publish
    app.register_blueprint(bp_publish)
    csrf.exempt(bp_publish)

    return app


@pytest.fixture
def csrf_client(csrf_app):
    """Create a test client with CSRF protection enabled."""
    return csrf_app.test_client()


class TestPublishEndpointWithCSRF2:
    """Integration tests for publish endpoint with CSRF enabled."""

    @pytest.fixture(autouse=True)
    def mock_is_allowed(self):
        """
        auto allow all
        """
        with patch("src.app_main.app_routes.publish.routes.is_allowed") as mocked:
            mocked.return_value = "medwiki.toolforge.org"
            yield mocked

    def test_options_preflight_with_csrf_enabled(self, csrf_client):
        """Test OPTIONS preflight request with CSRF enabled."""
        response = csrf_client.options("/publish")

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers

    def test_no_access_returns_403_with_csrf_enabled(self, csrf_client):
        """Test that no access error returns 403 even with CSRF enabled."""
        with (

            patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
        ):
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


class TestPublishEndpointWithDenyCSRF:
    """Integration tests for publish endpoint with CSRF enabled."""

    def test_cors_validation_still_works(self, csrf_client):
        """Test that CORS validation is applied before CSRF check."""
        with patch("src.app_main.app_routes.publish.routes.is_allowed") as mock_deny:
            mock_deny.return_value = None

            response = csrf_client.post(
                "/publish",
                data=json.dumps({"user": "TestUser", "title": "Test Page"}),
                content_type="application/json",
            )

            assert response.status_code == 403


class BasePublishTest:
    """Base class with shared fixtures for publish endpoint tests."""

    @pytest.fixture(autouse=True)
    def mock_is_allowed(self):
        with patch("src.app_main.app_routes.publish.routes.is_allowed") as mocked:
            mocked.return_value = "medwiki.toolforge.org"
            yield mocked

    @pytest.fixture(autouse=True)
    def mock_token(self):
        with patch("src.app_main.app_routes.publish.routes.get_user_token_by_username") as mock_get_token:
            token = MagicMock()
            token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = token
            self.mock_get_token = mock_get_token
            yield token


class TestSuccessFlows(BasePublishTest):
    """Successful edit flows."""

    def test_successful_edit_no_token_required(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.get_revid_db"),
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do"),
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_get_revid.return_value = "12345"
            mock_changes.return_value = "Modified content"
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}
            mock_reports_db.return_value = MagicMock()
            pages = MagicMock()
            pages.insert_page_target.return_value = {"execute_query": True}
            mock_pages_db.return_value = pages

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "TestUser", "title": "Test Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Original content",
                    "campaign": "test_campaign", "tr_type": "lead",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["edit"]["result"] == "Success"
            assert data["LinkToWikidata"]["result"] == "success"

    def test_fix_refs_applied(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_get_revid.return_value = "12345"
            mock_changes.return_value = "Fixed reference content"
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}
            mock_reports_db.return_value = MagicMock()
            pages = MagicMock()
            pages.insert_page_target.return_value = {"execute_query": True}
            mock_pages_db.return_value = pages

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "TestUser", "title": "Test Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Original content with references",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            if mock_to_do.call_args_list:
                assert mock_to_do.call_args_list[0][0][0].get("fix_refs") == "yes"

    def test_revid_resolution(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.get_revid_db") as mock_get_revid_db,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do"),
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_get_revid.return_value = "67890"
            mock_get_revid_db.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 99999}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}
            mock_reports_db.return_value = MagicMock()
            pages = MagicMock()
            pages.insert_page_target.return_value = {"execute_query": True}
            mock_pages_db.return_value = pages

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "TestUser", "title": "Test Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Content",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            mock_get_revid.assert_called_once_with("Source Page")


# ─── ب: منطق البيانات والـ Metadata ─────────────────────────────────────────

class TestMetadataLogic(BasePublishTest):
    """Data logic and metadata field tests."""

    def test_tr_type_parameter_passed_correctly(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.get_revid_db"),
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do"),
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}
            mock_reports_db.return_value = MagicMock()
            pages = MagicMock()
            pages.insert_page_target.return_value = {"execute_query": True}
            mock_pages_db.return_value = pages

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "TestUser", "title": "Test Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Content", "tr_type": "section",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            calls = pages.insert_page_target.call_args_list
            if calls:
                assert calls[0].kwargs.get("tr_type") == "section"

    def test_words_field_in_tab(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
            patch("src.app_main.app_routes.publish.worker.get_word_count") as mock_word_count,
        ):
            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}
            mock_word_count.return_value = 500
            mock_reports_db.return_value = MagicMock()
            pages = MagicMock()
            pages.insert_page_target.return_value = {"execute_query": True}
            mock_pages_db.return_value = pages

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "TestUser", "title": "Test Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Content",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            if mock_to_do.call_args_list:
                tab = mock_to_do.call_args_list[0][0][0]
                assert "words" in tab
                assert tab["words"] == 500

    def test_determine_hashtag_logic(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}
            mock_reports_db.return_value = MagicMock()
            pages = MagicMock()
            pages.insert_page_target.return_value = {"execute_query": True}
            mock_pages_db.return_value = pages

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "Mr. Ibrahem", "title": "Mr. Ibrahem/Test Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Content",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            if mock_to_do.call_args_list:
                summary = mock_to_do.call_args_list[0][0][0].get("summary", "")
                assert "#mdwikicx" not in summary or summary.endswith(" to:ar ")

    def test_empty_revid_fallback(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.get_revid_db") as mock_get_revid_db,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do") as mock_to_do,
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
            mock_get_revid.return_value = ""
            mock_get_revid_db.return_value = ""
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}
            mock_reports_db.return_value = MagicMock()
            pages = MagicMock()
            pages.insert_page_target.return_value = {"execute_query": True}
            mock_pages_db.return_value = pages

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "TestUser", "title": "Test Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Content", "revid": "99999",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            if mock_to_do.call_args_list:
                tab = mock_to_do.call_args_list[0][0][0]
                assert tab.get("revid") == "99999"
                assert "empty revid" in tab


# ─── ج: معالجة الأخطاء والـ Captcha ─────────────────────────────────────────

class TestErrorAndEdgeCases(BasePublishTest):
    """Error handling and captcha tests."""

    def test_captcha_handling(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.to_do"),
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
        ):
            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {
                "edit": {"captcha": {"id": "12345", "type": "image"}, "result": "Failure"}
            }
            mock_reports_db.return_value = MagicMock()

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "TestUser", "title": "Test Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Content",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            assert "captcha" in response.get_json()["edit"]

    def test_edit_error_handling(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.to_do"),
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
        ):
            mock_get_revid.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {
                "edit": {
                    "result": "Failure",
                    "error": {"code": "protectedpage", "info": "Page is protected"},
                }
            }
            mock_reports_db.return_value = MagicMock()

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "TestUser", "title": "Protected Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Content",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["edit"]["result"] == "Failure"
            assert "error" in data["edit"]


# ─── د: الحالات المعقدة ───────────────────────────────────────────────────────

class TestComplexWorkflows(BasePublishTest):
    """Complex multi-step workflows."""

    def test_wikidata_link_fallback_user(self, csrf_client):
        with (
            patch("src.app_main.app_routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.app_main.app_routes.publish.worker.do_changes_to_text") as mock_changes,
            patch("src.app_main.app_routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.app_main.app_routes.publish.worker.shouldAddedToWikidata") as mock_should_add,
            patch("src.app_main.app_routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.app_main.app_routes.publish.worker.to_do"),
            patch("src.app_main.app_routes.publish.worker.ReportsDB") as mock_reports_db,
            patch("src.app_main.app_routes.publish.worker.PagesDB") as mock_pages_db,
        ):
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
                    return self.mock_get_token.return_value
                elif username == "Mr. Ibrahem":
                    return fallback_token
                return None

            self.mock_get_token.side_effect = get_token_side_effect

            mock_reports_db.return_value = MagicMock()
            pages = MagicMock()
            pages.insert_page_target.return_value = {"execute_query": True}
            mock_pages_db.return_value = pages

            response = csrf_client.post(
                "/publish",
                data=json.dumps({
                    "user": "TestUser", "title": "Test Page", "target": "ar",
                    "sourcetitle": "Source Page", "text": "Content",
                }),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["edit"]["result"] == "Success"
            assert "fallback" in data["LinkToWikidata"]
