"""Unit tests for user_token_service module.

NOTE: These tests cover the service layer which acts as a thin wrapper around
the UserTokenDB class. The actual database operations are thoroughly tested in
test_db_user_tokens.py. These tests focus on:

- Singleton pattern (global _user_db caching)
- Error handling when database configuration is missing
- Delegation to underlying UserTokenDB methods
- Edge cases like empty/None inputs

The service layer provides:
- Lazy initialization of UserTokenDB with caching
- Configuration validation before DB operations
- Simplified API for common user token operations
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.domain.services.user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_store,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


class TestGetStore:
    """Tests for get_store function."""

    def test_returns_cached_instance_on_subsequent_calls(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service._user_db", mock_db)
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.has_db_config", lambda: True)

        result = get_store()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service._user_db", None)
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="UserTokenDB requires database configuration"):
            get_store()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new UserTokenDB is created when none cached."""
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service._user_db", None)
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.shared.domain.services.user_token_service.UserTokenDB") as MockUserTokenDB:
            MockUserTokenDB.return_value = mock_db_instance

            result = get_store()

            assert result is mock_db_instance
            MockUserTokenDB.assert_called_once()

    def test_caches_instance_after_first_creation(self, monkeypatch):
        """Test that created instance is cached for reuse."""
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service._user_db", None)
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.shared.domain.services.user_token_service.UserTokenDB") as MockUserTokenDB:
            MockUserTokenDB.return_value = mock_db_instance

            # First call
            result1 = get_store()
            # Second call should return cached instance
            result2 = get_store()

            assert result1 is result2 is mock_db_instance
            # UserTokenDB should only be instantiated once
            MockUserTokenDB.assert_called_once()


class TestUpsertUserToken:
    """Tests for upsert_user_token function."""

    def test_delegates_to_store_upsert(self, monkeypatch):
        """Test that function delegates to store.upsert."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        upsert_user_token(
            user_id=12345,
            username="TestUser",
            access_key="test_key",
            access_secret="test_secret",
        )

        mock_store.upsert.assert_called_once_with(12345, "TestUser", "test_key", "test_secret")


class TestGetUserToken:
    """Tests for get_user_token function."""

    def test_returns_none_for_empty_user_id(self):
        """Test that None is returned for empty user_id."""
        result = get_user_token("")
        assert result is None

        result = get_user_token(None)
        assert result is None

        # Note: 0 is treated as falsy and returns None
        # This is the current behavior of the service layer
        result = get_user_token(0)
        assert result is None

    def test_returns_record_when_found(self, monkeypatch):
        """Test that record is returned when found."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store._fetch_by_id.return_value = mock_record
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        result = get_user_token(12345)

        assert result is mock_record
        mock_store._fetch_by_id.assert_called_once_with(12345)

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""
        mock_store = MagicMock()
        mock_store._fetch_by_id.side_effect = LookupError("Not found")
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        result = get_user_token(99999)

        assert result is None


class TestDeleteUserToken:
    """Tests for delete_user_token function."""

    def test_returns_none_for_empty_user_id(self, monkeypatch):
        """Test that None is returned for empty user_id."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        result = delete_user_token("")
        assert result is None

        result = delete_user_token(None)
        assert result is None

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        delete_user_token(12345)

        mock_store.delete.assert_called_once_with(12345)


class TestGetUserTokenByUsername:
    """Tests for get_user_token_by_username function."""

    def test_returns_none_for_empty_username(self):
        """Test that None is returned for empty username."""
        result = get_user_token_by_username("")
        assert result is None

        result = get_user_token_by_username("   ")
        assert result is None

    def test_strips_whitespace_from_username(self, monkeypatch):
        """Test that username is stripped of whitespace."""
        mock_store = MagicMock()
        mock_store._fetch_by_username.return_value = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        get_user_token_by_username("  TestUser  ")

        mock_store._fetch_by_username.assert_called_once_with("TestUser")

    def test_returns_record_when_found(self, monkeypatch):
        """Test that record is returned when found."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store._fetch_by_username.return_value = mock_record
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        result = get_user_token_by_username("TestUser")

        assert result is mock_record

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""
        mock_store = MagicMock()
        mock_store._fetch_by_username.side_effect = LookupError("Not found")
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        result = get_user_token_by_username("NonExistent")

        assert result is None


class TestDeleteUserTokenByUsername:
    """Tests for delete_user_token_by_username function."""

    def test_returns_none_for_empty_username(self, monkeypatch):
        """Test that None is returned for empty username."""
        mock_store = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        result = delete_user_token_by_username("")
        assert result is None

        result = delete_user_token_by_username("   ")
        assert result is None

    def test_deletes_by_user_id_when_found(self, monkeypatch):
        """Test that token is deleted by user_id when username found."""
        mock_store = MagicMock()
        mock_store.get_user_id.return_value = 12345
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        delete_user_token_by_username("TestUser")

        mock_store.get_user_id.assert_called_once_with("TestUser")
        mock_store.delete.assert_called_once_with(12345)

    def test_skips_delete_when_user_not_found(self, monkeypatch):
        """Test that delete is skipped when username not found."""
        mock_store = MagicMock()
        mock_store.get_user_id.return_value = None
        monkeypatch.setattr("src.app_main.shared.domain.services.user_token_service.get_store", lambda: mock_store)

        delete_user_token_by_username("NonExistent")

        mock_store.get_user_id.assert_called_once_with("NonExistent")
        mock_store.delete.assert_not_called()
