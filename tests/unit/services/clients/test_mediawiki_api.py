"""Tests for clients.mediawiki_api module."""

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest


@dataclass
class MockMediaWikiApiDeps:
    post_params: MagicMock
    requests: MagicMock


@pytest.fixture
def mock_mediawiki_deps(monkeypatch: pytest.MonkeyPatch) -> MockMediaWikiApiDeps:
    """Fixture to bundle and set up common patches for mediawiki api tests."""
    _client = "src.main_app.services.clients.mediawiki_api"
    _oauth = "src.main_app.services.clients.oauth_client"

    mock_post_params = MagicMock()
    mock_requests = MagicMock()

    monkeypatch.setattr(f"{_client}.post_params", mock_post_params)
    monkeypatch.setattr(f"{_client}.requests", mock_requests)
    monkeypatch.setattr(f"{_oauth}.OAuthClient.post_params", mock_post_params)

    return MockMediaWikiApiDeps(
        post_params=mock_post_params,
        requests=mock_requests,
    )


class TestPublishDoEdit:
    """Tests for publish_do_edit function and MediaWikiApiClient."""

    def test_returns_edit_result_on_success(self, mock_mediawiki_deps: MockMediaWikiApiDeps):
        """Test that edit result is returned on success."""
        mock_mediawiki_deps.post_params.return_value = '{"edit": {"result": "Success", "newrevid": 12345}}'

        from src.main_app.services.clients.mediawiki_api import MediaWikiApiClient

        result = MediaWikiApiClient.publish_do_edit(
            {"action": "edit", "title": "Test Page"},
            "en",
            "access_key",
            "access_secret",
        )

        assert result["edit"]["result"] == "Success"
        assert result["edit"]["newrevid"] == 12345

    def test_returns_error_on_failed_edit(self, mock_mediawiki_deps: MockMediaWikiApiDeps):
        """Test that error is returned on failed edit."""
        mock_mediawiki_deps.post_params.return_value = (
            '{"error": {"code": "protectedpage", "info": "Page is protected"}}'
        )

        from src.main_app.services.clients.mediawiki_api import MediaWikiApiClient

        result = MediaWikiApiClient.publish_do_edit(
            {"action": "edit", "title": "Protected Page"},
            "en",
            "access_key",
            "access_secret",
        )

        assert "error" in result
        assert result["error"]["code"] == "protectedpage"

    def test_returns_empty_dict_on_empty_response(self, mock_mediawiki_deps: MockMediaWikiApiDeps):
        """Test that empty dict is returned on empty response."""
        mock_mediawiki_deps.post_params.return_value = ""

        from src.main_app.services.clients.mediawiki_api import MediaWikiApiClient

        result = MediaWikiApiClient.publish_do_edit(
            {"action": "edit", "title": "Test Page"},
            "en",
            "access_key",
            "access_secret",
        )

        assert result == {}

    def test_returns_error_on_invalid_json(self, mock_mediawiki_deps: MockMediaWikiApiDeps):
        """Test that error is returned on invalid JSON response."""
        mock_mediawiki_deps.post_params.return_value = "not valid json"

        from src.main_app.services.clients.mediawiki_api import MediaWikiApiClient

        result = MediaWikiApiClient.publish_do_edit(
            {"action": "edit", "title": "Test Page"},
            "en",
            "access_key",
            "access_secret",
        )

        assert "error" in result

    def test_constructs_correct_domain_url(self, mock_mediawiki_deps: MockMediaWikiApiDeps):
        """Test that the correct domain URL is constructed."""
        mock_mediawiki_deps.post_params.return_value = '{"edit": {"result": "Success"}}'

        from src.main_app.services.clients.mediawiki_api import MediaWikiApiClient

        MediaWikiApiClient.publish_do_edit(
            {"action": "edit", "title": "Test Page"},
            "ar",
            "access_key",
            "access_secret",
        )

        # Verify the domain was passed correctly
        call_args = mock_mediawiki_deps.post_params.call_args
        assert call_args[0][1] == "https://ar.wikipedia.org"


class TestGetTitleInfo:
    """Tests for get_title_info function and MediaWikiApiClient."""

    def test_returns_page_info_on_success(self, mock_mediawiki_deps: MockMediaWikiApiDeps):
        """Test that page info is returned on success."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "query": {"pages": [{"pageid": 123, "title": "Test Page", "missing": False}]}
        }
        mock_mediawiki_deps.requests.get.return_value = mock_response

        from src.main_app.services.clients.mediawiki_api import MediaWikiApiClient

        result = MediaWikiApiClient.get_title_info("Test Page", "en")

        assert result is not None
        assert result["pageid"] == 123
        assert result["title"] == "Test Page"

    def test_returns_none_on_error(self, mock_mediawiki_deps: MockMediaWikiApiDeps):
        """Test that None is returned on error."""
        mock_mediawiki_deps.requests.get.side_effect = Exception("Network error")

        from src.main_app.services.clients.mediawiki_api import MediaWikiApiClient

        result = MediaWikiApiClient.get_title_info("Test Page", "en")

        assert result is None
