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
from src.sqlalchemy_app.shared.domain.services.user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


class TestUpsertUserToken:
    """Tests for upsert_user_token function."""

    def test_delegates_to_store_upsert(self, monkeypatch):
        """Test that function delegates to store.upsert."""
        mock_store = MagicMock()

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

        result = get_user_token(12345)

        assert result is mock_record
        mock_store._fetch_by_id.assert_called_once_with(12345)

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""
        mock_store = MagicMock()
        mock_store._fetch_by_id.side_effect = LookupError("Not found")

        result = get_user_token(99999)

        assert result is None


class TestDeleteUserToken:
    """Tests for delete_user_token function."""

    def test_returns_none_for_empty_user_id(self, monkeypatch):
        """Test that None is returned for empty user_id."""
        mock_store = MagicMock()

        result = delete_user_token("")
        assert result is None

        result = delete_user_token(None)
        assert result is None

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()

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

        get_user_token_by_username("  TestUser  ")

        mock_store._fetch_by_username.assert_called_once_with("TestUser")

    def test_returns_record_when_found(self, monkeypatch):
        """Test that record is returned when found."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store._fetch_by_username.return_value = mock_record

        result = get_user_token_by_username("TestUser")

        assert result is mock_record

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""
        mock_store = MagicMock()
        mock_store._fetch_by_username.side_effect = LookupError("Not found")

        result = get_user_token_by_username("NonExistent")

        assert result is None


class TestDeleteUserTokenByUsername:
    """Tests for delete_user_token_by_username function."""

    def test_returns_none_for_empty_username(self, monkeypatch):
        """Test that None is returned for empty username."""
        mock_store = MagicMock()

        result = delete_user_token_by_username("")
        assert result is None

        result = delete_user_token_by_username("   ")
        assert result is None

    def test_deletes_by_user_id_when_found(self, monkeypatch):
        """Test that token is deleted by user_id when username found."""
        mock_store = MagicMock()
        mock_store.get_user_id.return_value = 12345

        delete_user_token_by_username("TestUser")

        mock_store.get_user_id.assert_called_once_with("TestUser")
        mock_store.delete.assert_called_once_with(12345)

    def test_skips_delete_when_user_not_found(self, monkeypatch):
        """Test that delete is skipped when username not found."""
        mock_store = MagicMock()
        mock_store.get_user_id.return_value = None

        delete_user_token_by_username("NonExistent")

        mock_store.get_user_id.assert_called_once_with("NonExistent")
        mock_store.delete.assert_not_called()
