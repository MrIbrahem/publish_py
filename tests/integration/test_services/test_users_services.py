"""Integration tests for users_services module.

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

from src.app_main.services.users_services import (
    delete_user_token,
    delete_user_token_by_username,
    get_store,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


class TestUserServiceIntegration:
    """Integration tests for user token service."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self, monkeypatch):
        """Reset the singleton before each test."""
        monkeypatch.setattr("src.app_main.services.users_services._user_db", None)

    def test_full_token_lifecycle(self, monkeypatch):
        """Test complete CRUD lifecycle through service layer."""
        # Setup mock DB
        mock_db = MagicMock()
        mock_record = MagicMock()
        mock_record.user_id = 12345
        mock_record.username = "TestUser"

        with patch("src.app_main.services.users_services.UserTokenDB") as MockUserTokenDB:
            MockUserTokenDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.services.users_services.has_db_config", lambda: True)

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

    def test_service_reuses_db_instance(self, monkeypatch):
        """Test that service reuses DB instance across operations."""
        mock_db = MagicMock()

        with patch("src.app_main.services.users_services.UserTokenDB") as MockUserTokenDB:
            MockUserTokenDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.services.users_services.has_db_config", lambda: True)

            # Multiple operations
            get_user_token(1)
            get_user_token(2)
            upsert_user_token(user_id=3, username="Test", access_key="key", access_secret="secret")

            # UserTokenDB should only be instantiated once (singleton pattern)
            MockUserTokenDB.assert_called_once()

    def test_username_lookup_integration(self, monkeypatch):
        """Test username-based operations integrate correctly."""
        mock_db = MagicMock()
        mock_record = MagicMock()
        mock_record.user_id = 12345

        with patch("src.app_main.services.users_services.UserTokenDB") as MockUserTokenDB:
            MockUserTokenDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.services.users_services.has_db_config", lambda: True)

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

        with patch("src.app_main.services.users_services.UserTokenDB") as MockUserTokenDB:
            MockUserTokenDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.services.users_services.has_db_config", lambda: True)

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

        with patch("src.app_main.services.users_services.UserTokenDB") as MockUserTokenDB:
            MockUserTokenDB.return_value = mock_db
            monkeypatch.setattr("src.app_main.services.users_services.has_db_config", lambda: True)

            # Setup DB to raise LookupError
            mock_db._fetch_by_id.side_effect = LookupError("User not found")
            mock_db._fetch_by_username.side_effect = LookupError("User not found")

            # Service should return None, not propagate exception
            assert get_user_token(99999) is None
            assert get_user_token_by_username("NonExistent") is None


class TestServiceErrorHandling:
    """Tests for service layer error handling integration."""

    def test_handles_db_initialization_failure(self, monkeypatch):
        """Test service handles DB initialization failure."""
        monkeypatch.setattr("src.app_main.services.users_services._user_db", None)
        monkeypatch.setattr("src.app_main.services.users_services.has_db_config", lambda: True)

        with patch("src.app_main.services.users_services.UserTokenDB") as MockUserTokenDB:
            MockUserTokenDB.side_effect = Exception("DB Connection Failed")

            with pytest.raises(RuntimeError, match="Unable to initialize UserTokenDB"):
                get_store()

    def test_validates_config_before_db_access(self, monkeypatch):
        """Test service validates config before attempting DB operations."""
        monkeypatch.setattr("src.app_main.services.users_services._user_db", None)
        monkeypatch.setattr("src.app_main.services.users_services.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="UserTokenDB requires database configuration"):
            get_store()
