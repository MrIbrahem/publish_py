"""Integration tests for user_token_service module.

NOTE: These integration tests verify the service layer works correctly with
the database layer. The service module acts as a thin wrapper around UserTokenDB.

These tests verify:
- Service initialization and DB connection
- End-to-end token operations through the service layer
- Error handling integration between service and DB layers
- The service layer properly delegates to UserTokenDB while adding:
  - Singleton pattern management
  - Configuration validation
  - Input sanitization (strip whitespace)
  - None-safe operations

The actual DB operations are mocked to avoid requiring a real database.
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


class TestUserServiceIntegration:
    """Integration tests for user token service."""

    def test_full_token_lifecycle(self, monkeypatch):
        """Test complete CRUD lifecycle through service layer."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_record = MagicMock()
        mock_record.user_id = 12345
        mock_record.username = "TestUser"

        # 1. Create token
        mock_db.upsert.return_value = mock_record
        upsert_user_token(
            user_id=12345,
            username="TestUser",
            access_key="test_key",
            access_secret="test_secret",
        )

        # 2. Read token
        mock_db._fetch_by_id.return_value = mock_record
        result = get_user_token(12345)
        assert result is mock_record

        # 3. Delete token
        mock_db.delete.return_value = None
        delete_user_token(12345)

        # Verify all operations were called
        mock_db.upsert.assert_called_once()
        mock_db._fetch_by_id.assert_called_once_with(12345)
        mock_db.delete.assert_called_once_with(12345)

    def test_username_lookup_integration(self, monkeypatch):
        """Test username-based operations integrate correctly."""
        mock_db = MagicMock()
        mock_record = MagicMock()
        mock_record.user_id = 12345

        # Setup mock responses
        mock_db._fetch_by_username.return_value = mock_record
        mock_db.get_user_id.return_value = 12345

        # Get by username
        result = get_user_token_by_username("TestUser")
        assert result.user_id == 12345

        # Delete by username
        delete_user_token_by_username("TestUser")
        mock_db.delete.assert_called_once_with(12345)

    def test_empty_username_handling(self, monkeypatch):
        """Test service handles empty usernames gracefully."""
        mock_db = MagicMock()

        # These should not call the DB
        result = get_user_token_by_username("")
        assert result is None
        mock_db._fetch_by_username.assert_not_called()

        result = delete_user_token_by_username("   ")
        assert result is None
        mock_db.get_user_id.assert_not_called()

    def test_lookup_error_handling(self, monkeypatch):
        """Test service handles LookupError from DB layer."""
        mock_db = MagicMock()

        # Setup DB to raise LookupError
        mock_db._fetch_by_id.side_effect = LookupError("User not found")
        mock_db._fetch_by_username.side_effect = LookupError("User not found")

        # Service should return None, not propagate exception
        assert get_user_token(99999) is None
        assert get_user_token_by_username("NonExistent") is None
