"""Integration tests for publish endpoint with CSRF protection enabled.

These tests verify the full publish flow when WTF_CSRF_ENABLED=True,
using a configuration similar to ProductionConfig.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask


@pytest.fixture
def csrf_app() -> Flask:
    """Create a Flask app with CSRF protection enabled (like Production)."""
    import os

    os.environ.setdefault("CORS_ALLOWED_DOMAINS", "medwiki.toolforge.org,mdwikicx.toolforge.org")

    from flask import Flask
    from flask_wtf.csrf import CSRFProtect

    app = Flask(__name__)
    app.config.update(
        {
            "SECRET_KEY": "test-secret-key-for-csrf-integration-tests",
            "WTF_CSRF_ENABLED": True,
            "WTF_CSRF_SSL_STRICT": False,
            "TESTING": True,
            "CORS_DISABLED": False,
        }
    )
    app.url_map.strict_slashes = False

    csrf = CSRFProtect(app)
    from src.sqlalchemy_app.public.routes.publish.routes import bp_publish

    app.register_blueprint(bp_publish)
    csrf.exempt(bp_publish)

    return app


@pytest.fixture
def csrf_client(csrf_app):
    """Create a test client with CSRF protection enabled."""
    return csrf_app.test_client()


class TestPublishEndpointWithDenyCSRF:
    """Integration tests for publish endpoint with CSRF enabled."""

    def test_cors_validation_still_works(self, mock_is_denied, csrf_client):
        """Test that CORS validation is applied before CSRF check."""
        with (
            patch("src.sqlalchemy_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.sqlalchemy_app.public.routes.publish.worker.add_report") as mock_load_reports_db,
        ):
            mock_get_token.return_value = None
            mock_load_reports_db_instance = MagicMock()
            mock_load_reports_db.return_value = mock_load_reports_db_instance

            response = csrf_client.post(
                "/publish",
                data=json.dumps({"user": "TestUser", "title": "Test Page"}),
                content_type="application/json",
            )

            assert response.status_code == 403


class TestPublishEndpointWithCSRF2:
    """Integration tests for publish endpoint with CSRF enabled."""

    def test_options_preflight_with_csrf_enabled(self, mock_is_allowed, csrf_client):
        """Test OPTIONS preflight request with CSRF enabled."""
        response = csrf_client.options(
            "/publish",
            base_url="https://medwiki.toolforge.org",
            headers={"Origin": "https://medwiki.toolforge.org"},
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers

    def test_no_access_returns_403_with_csrf_enabled(self, mock_is_allowed, csrf_client):
        """Test that no access error returns 403 even with CSRF enabled."""
        with (
            patch("src.sqlalchemy_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token,
            patch("src.sqlalchemy_app.public.routes.publish.worker.to_do") as mock_to_do,
            patch("src.sqlalchemy_app.public.routes.publish.worker.add_report") as mock_load_reports_db,
        ):
            mock_get_token.return_value = None

            mock_reports_instance = MagicMock()
            mock_load_reports_db.return_value = mock_reports_instance

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


class BasePublishTest:
    """Base class with shared fixtures for publish endpoint tests."""

    @pytest.fixture(autouse=True)
    def mock_get_campaign_category(mocker):
        with patch("src.sqlalchemy_app.public.routes.publish.worker.get_campaign_category") as mocked:
            mocked.return_value = None
            yield mocked

    @pytest.fixture(autouse=True)
    def mock_is_allowed(self):
        with patch("src.sqlalchemy_app.shared.core.cors.is_allowed") as mocked:
            mocked.return_value = "medwiki.toolforge.org"
            yield mocked

    @pytest.fixture(autouse=True)
    def mock_token(self):
        with patch("src.sqlalchemy_app.public.routes.publish.routes.get_user_token_by_username") as mock_get_token:
            token = MagicMock()
            token.decrypted.return_value = ("access_key", "access_secret")
            mock_get_token.return_value = token
            self.mock_get_token = mock_get_token
            yield token

    @pytest.fixture
    def common_patches(self):
        """Patch the full happy-path stack and expose mocks as a dict."""
        with (
            patch("src.sqlalchemy_app.public.routes.publish.worker.get_revid") as mock_get_revid,
            patch("src.sqlalchemy_app.public.routes.publish.worker.get_revid_db") as mock_get_revid_db,
            patch("src.sqlalchemy_app.public.routes.publish.worker.do_changes_to_text_with_settings") as mock_changes,
            patch("src.sqlalchemy_app.public.routes.publish.worker.publish_do_edit") as mock_edit,
            patch("src.sqlalchemy_app.public.routes.publish.worker.link_to_wikidata") as mock_link,
            patch("src.sqlalchemy_app.public.routes.publish.worker.to_do") as mock_to_do,
            patch("src.sqlalchemy_app.public.routes.publish.worker.add_report") as mock_load_reports_db,
            patch("src.sqlalchemy_app.public.routes.publish.worker.shouldAddedToWikidata") as mock_should_add,
            patch("src.sqlalchemy_app.public.routes.publish.worker.find_exists_or_update_page") as mock_find_exists,
            patch(
                "src.sqlalchemy_app.public.routes.publish.worker.find_exists_or_update_user_page"
            ) as mock_user_find_exists,
            patch("src.sqlalchemy_app.public.routes.publish.worker.insert_page_target") as mock_insert_page,
            patch("src.sqlalchemy_app.public.routes.publish.worker.insert_user_page_target") as mock_insert_user_page,
        ):
            # ── defaults that cover the happy path ──────────────────────────
            mock_get_revid.return_value = "12345"
            mock_get_revid_db.return_value = "12345"
            mock_changes.return_value = None
            mock_edit.return_value = {"edit": {"result": "Success", "newrevid": 67890}}
            mock_link.return_value = {"result": "success", "qid": "Q123"}
            mock_should_add.return_value = True
            mock_find_exists.return_value = False
            mock_insert_page.return_value = True
            mock_insert_user_page.return_value = True

            mock_load_reports_db.return_value = MagicMock()

            yield {
                "get_revid": mock_get_revid,
                "get_revid_db": mock_get_revid_db,
                "changes": mock_changes,
                "edit": mock_edit,
                "link": mock_link,
                "to_do": mock_to_do,
                "add_report": mock_load_reports_db,
                "should_add": mock_should_add,
                "find_exists_or_update_page": mock_find_exists,
                "find_exists_or_update_user_page": mock_user_find_exists,
                "insert_page_target": mock_insert_page,
                "insert_user_page_target": mock_insert_user_page,
            }

    # ── helper ──────────────────────────────────────────────────────────────
    def _post(self, client, payload: dict):
        return client.post(
            "/publish",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def _default_payload(self, **overrides):
        base = {
            "user": "TestUser",
            "title": "Test Page",
            "target": "ar",
            "sourcetitle": "Source Page",
            "text": "Content",
        }
        return {**base, **overrides}


class TestSuccessFlows(BasePublishTest):
    def test_successful_edit(self, csrf_client, common_patches):
        # common_patches يغطي الـ happy-path بالكامل — لا شيء إضافي هنا
        response = self._post(
            csrf_client,
            self._default_payload(
                campaign="test_campaign",
                translate_type="lead",
            ),
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["edit"]["result"] == "Success"
        assert data["LinkToWikidata"]["result"] == "success"

    def test_fix_refs_applied(self, csrf_client, common_patches):
        # نُعدّل فقط القيمة التي تختلف عن الـ default
        common_patches["changes"].return_value = "Fixed reference content"

        response = self._post(
            csrf_client,
            self._default_payload(
                text="Original content with references",
            ),
        )

        assert response.status_code == 200
        to_do_calls = common_patches["to_do"].call_args_list
        assert to_do_calls[0][0][0].get("fix_refs") == "yes"

    def test_revid_resolution(self, csrf_client, common_patches):
        common_patches["get_revid"].return_value = "67890"
        common_patches["get_revid_db"].return_value = "12345"

        response = self._post(csrf_client, self._default_payload())

        assert response.status_code == 200
        common_patches["get_revid"].assert_called_once_with("Source Page")


class TestMetadataLogic(BasePublishTest):
    def test_tr_type_passed_correctly(self, csrf_client, common_patches):
        response = self._post(csrf_client, self._default_payload(translate_type="all"))

        assert response.status_code == 200
        calls = common_patches["insert_page_target"].call_args_list
        assert calls[0].kwargs.get("translate_type") == "all"

    def test_bad_tr_type(self, csrf_client, common_patches):
        response = self._post(csrf_client, self._default_payload(translate_type="test"))

        assert response.status_code == 400
        calls = common_patches["insert_page_target"].call_args_list
        assert calls == []

    def test_words_field_in_tab(self, csrf_client, common_patches):
        with (patch("src.sqlalchemy_app.public.routes.publish.worker.get_word_count") as mock_word_count,):
            mock_word_count.return_value = 500

            response = self._post(csrf_client, self._default_payload())

        assert response.status_code == 200
        to_do_calls = common_patches["to_do"].call_args_list
        tab = to_do_calls[0][0][0]
        assert "words" in tab
        assert tab["words"] == 500

    def test_hashtag_logic(self, csrf_client, common_patches):
        response = self._post(
            csrf_client,
            self._default_payload(
                user="Mr. Ibrahem",
                title="Mr. Ibrahem/Test Page",
            ),
        )

        assert response.status_code == 200
        to_do_calls = common_patches["to_do"].call_args_list
        summary = to_do_calls[0][0][0].get("summary", "")
        assert "#mdwikicx" not in summary or summary.endswith(" to:ar ")

    def test_empty_revid_fallback(self, csrf_client, common_patches):
        # نُعدّل الـ revid ليكون فارغاً
        common_patches["get_revid"].return_value = ""
        common_patches["get_revid_db"].return_value = ""

        response = self._post(csrf_client, self._default_payload(revid="99999"))

        assert response.status_code == 200
        to_do_calls = common_patches["to_do"].call_args_list
        tab = to_do_calls[0][0][0]
        assert tab.get("revid") == "99999"
        assert "empty revid" in tab


class TestErrorAndEdgeCases(BasePublishTest):
    def test_captcha_handling(self, csrf_client, common_patches):
        # نُعدّل الـ edit ليعيد captcha بدلاً من Success
        common_patches["edit"].return_value = {
            "edit": {"captcha": {"id": "12345", "type": "image"}, "result": "Failure"}
        }

        response = self._post(csrf_client, self._default_payload())

        assert response.status_code == 200
        assert "captcha" in response.get_json()["edit"]

    def test_edit_error_handling(self, csrf_client, common_patches):
        common_patches["edit"].return_value = {
            "edit": {
                "result": "Failure",
                "error": {"code": "protectedpage", "info": "Page is protected"},
            }
        }

        response = self._post(csrf_client, self._default_payload(title="Protected Page"))

        assert response.status_code == 200
        data = response.get_json()
        assert data["edit"]["result"] == "Failure"
        assert "error" in data["edit"]


class TestComplexWorkflows(BasePublishTest):
    def test_wikidata_link_fallback_user(self, csrf_client, common_patches):
        with (patch("src.sqlalchemy_app.public.routes.publish.worker.shouldAddedToWikidata") as mock_should_add,):
            mock_should_add.return_value = True

            # أول استدعاء يفشل، الثاني ينجح عبر fallback user
            common_patches["link"].side_effect = [
                {"error": "get_csrftoken failed", "qid": "Q123"},
                {"result": "success", "qid": "Q123"},
            ]

            fallback_token = MagicMock()
            fallback_token.decrypted.return_value = ("fallback_key", "fallback_secret")

            def get_token_side_effect(username):
                if username == "Mr. Ibrahem":
                    return fallback_token
                return self.mock_get_token.return_value

            self.mock_get_token.side_effect = get_token_side_effect

            with patch(
                "src.sqlalchemy_app.public.routes.publish.worker.get_user_token_by_username",
                side_effect=get_token_side_effect,
            ):
                response = self._post(csrf_client, self._default_payload())

        assert response.status_code == 200
        data = response.get_json()
        assert data["edit"]["result"] == "Success"
        assert "fallback" in data["LinkToWikidata"]
