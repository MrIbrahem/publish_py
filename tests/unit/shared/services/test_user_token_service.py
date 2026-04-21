from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.db_models import UserTokenRecord
from src.sqlalchemy_app.sqlalchemy_models import _UserTokenRecord
from src.sqlalchemy_app.shared.services.user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


def test_user_token_workflow():
    upsert_user_token(
        user_id=12345, username="ExampleWikiEditor", access_key="oauth_key_123", access_secret="oauth_secret_456"
    )
    t = get_user_token(12345)
    assert t.username == "ExampleWikiEditor"
    assert get_user_token_by_username("ExampleWikiEditor").user_id == 12345
    delete_user_token_by_username("ExampleWikiEditor")
    assert get_user_token(12345) is None
    upsert_user_token(user_id=67890, username="TrustedContributor", access_key="key2", access_secret="secret2")
    delete_user_token(67890)
    assert get_user_token(67890) is None


class TestUpsertUserToken:
    """Tests for upsert_user_token function."""

    def test_inserts_new_token(self, monkeypatch):
        """Test that function inserts a new token."""
        upsert_user_token(user_id=1, username="GlobalAdmin", access_key="k1", access_secret="s1")
        record = get_user_token(1)
        assert record.username == "GlobalAdmin"

    def test_updates_existing_token(self, monkeypatch):
        """Test that function updates an existing token."""
        upsert_user_token(user_id=1, username="GlobalAdmin", access_key="k1", access_secret="s1")
        upsert_user_token(user_id=1, username="GlobalAdmin_Updated", access_key="k2", access_secret="s2")
        record = get_user_token(1)
        assert record.username == "GlobalAdmin_Updated"

    def test_raises_error_if_no_username(self, monkeypatch):
        with pytest.raises(ValueError, match="Username is required"):
            upsert_user_token(user_id=1, username="", access_key="k", access_secret="s")


class TestGetUserToken:
    """Tests for get_user_token function."""

    def test_returns_none_for_empty_user_id(self):
        """Test that None is returned for empty user_id."""
        assert get_user_token(None) is None
        assert get_user_token("") is None

    def test_returns_record_when_found(self, monkeypatch):
        """Test that record is returned when found."""
        upsert_user_token(user_id=100, username="MedicineBot", access_key="k1", access_secret="s1")
        record = get_user_token(100)
        assert isinstance(record, UserTokenRecord)
        assert record.user_id == 100

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""
        assert get_user_token(999999) is None


class TestDeleteUserToken:
    """Tests for delete_user_token function."""

    def test_returns_none_for_empty_user_id(self, monkeypatch):
        """Test that None is returned for empty user_id."""
        assert delete_user_token(None) is None

    def test_deletes_the_token(self, monkeypatch):
        """Test that function deletes the token."""
        upsert_user_token(user_id=200, username="TranslatorHelper", access_key="k1", access_secret="s1")
        delete_user_token(200)
        assert get_user_token(200) is None


class TestGetUserTokenByUsername:
    """Tests for get_user_token_by_username function."""

    def test_returns_none_for_empty_username(self):
        """Test that None is returned for empty username."""
        assert get_user_token_by_username("") is None
        assert get_user_token_by_username("   ") is None

    def test_strips_whitespace_from_username(self, monkeypatch):
        """Test that username is stripped of whitespace."""
        upsert_user_token(user_id=300, username="CleanUser", access_key="k1", access_secret="s1")
        assert get_user_token_by_username("  CleanUser  ").user_id == 300

    def test_returns_record_when_found(self, monkeypatch):
        """Test that record is returned when found."""
        upsert_user_token(user_id=400, username="ActiveBureaucrat", access_key="k1", access_secret="s1")
        assert get_user_token_by_username("ActiveBureaucrat").user_id == 400

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""
        assert get_user_token_by_username("GhostEditor") is None


class TestDeleteUserTokenByUsername:
    """Tests for delete_user_token_by_username function."""

    def test_returns_none_for_empty_username(self, monkeypatch):
        """Test that None is returned for empty username."""
        assert delete_user_token_by_username("") is None

    def test_deletes_by_user_id_when_found(self, monkeypatch):
        """Test that token is deleted by user_id when username found."""
        upsert_user_token(user_id=500, username="OneTimeUser", access_key="k1", access_secret="s1")
        delete_user_token_by_username("OneTimeUser")
        assert get_user_token(500) is None

    def test_skips_delete_when_user_not_found(self, monkeypatch):
        """Test that delete is skipped when username not found."""
        delete_user_token_by_username("NonExistentUser")
