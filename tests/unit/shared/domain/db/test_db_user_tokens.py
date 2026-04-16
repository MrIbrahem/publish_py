"""Unit tests for db.db_user_tokens module.

Tests for UserToken database operations.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.config import DbConfig
from src.app_main.shared.domain.db.db_user_tokens import (
    UserTokenDB,
    UserTokenRecord,
)


@pytest.fixture
def db_config() -> DbConfig:
    """Fixture for DbConfig instance."""
    return DbConfig(
        db_name="test_db",
        db_host="localhost",
        db_user="user",
        db_password="pass",
    )


class TestUserTokenDBMarkTokenUsed:
    """
    Tests for UserTokenDB class mark_token_used method.
    """

    def test_mark_token_used_updates_timestamp(self, monkeypatch, db_config):
        """Test that mark_token_used updates the last_used_at timestamp."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "User1", "access_token": b"t1", "access_secret": b"s1"}
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        result = token_db.mark_token_used(1)

        mock_db.execute_query.assert_called_with(
            "UPDATE user_tokens SET last_used_at = CURRENT_TIMESTAMP WHERE user_id = %s",
            (1,),
        )
        assert result is None


class TestUserTokenDBGetUserId:
    """Tests for UserTokenDB class get_user_id method."""

    def test_get_user_id_returns_id_when_found(self, monkeypatch, db_config):
        """Test that get_user_id returns user_id when username found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"user_id": 12345}]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        result = token_db.get_user_id("TestUser")

        assert result == 12345
        mock_db.fetch_query_safe.assert_called_with(
            "SELECT user_id FROM user_tokens WHERE username = %s",
            ("TestUser",),
        )

    def test_get_user_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that get_user_id returns None when username not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        result = token_db.get_user_id("MissingUser")

        assert result is None


class TestUserTokenDB:
    """Tests for UserTokenDB class."""

    def test_fetch_by_id_raises_lookup_error_when_not_found(self, monkeypatch, db_config):
        """Test that _fetch_by_id raises LookupError when user not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        with pytest.raises(LookupError, match="User user_id 999 was not found"):
            token_db._fetch_by_id(999)

    def test_fetch_by_username_raises_lookup_error_when_not_found(self, monkeypatch, db_config):
        """Test that _fetch_by_username raises LookupError when user not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        with pytest.raises(LookupError, match="User MissingUser was not found"):
            token_db._fetch_by_username("MissingUser")

    def test_list_returns_all_records(self, monkeypatch, db_config):
        """Test that list returns all user token records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "User1", "access_token": b"t1", "access_secret": b"s1"},
            {"user_id": 2, "username": "User2", "access_token": b"t2", "access_secret": b"s2"},
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        result = token_db.list()

        assert len(result) == 2
        assert all(isinstance(r, UserTokenRecord) for r in result)
        assert result[0].user_id == 1
        assert result[1].user_id == 2

    def test_upsert_requires_non_empty_username(self, monkeypatch, db_config):
        """Test that upsert requires non-empty username."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        with pytest.raises(ValueError, match="Username is required"):
            token_db.upsert(1, "", "token", "secret")

        with pytest.raises(ValueError, match="Username is required"):
            token_db.upsert(1, "   ", "token", "secret")

    @patch("src.app_main.shared.domain.db.db_user_tokens.encrypt_value")
    def test_upsert_executes_insert_query(self, mock_encrypt, monkeypatch, db_config):
        """Test that upsert executes correct INSERT query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "TestUser", "access_token": b"enc_token", "access_secret": b"enc_secret"}
        ]
        mock_encrypt.side_effect = [b"enc_token", b"enc_secret"]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        token_db.upsert(1, "TestUser", "access_key", "access_secret")

        # Check that execute_query_safe was called with INSERT
        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO user_tokens" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]

    def test_delete_raises_lookup_error_when_not_found(self, monkeypatch, db_config):
        """Test that delete raises LookupError when user not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        with pytest.raises(LookupError, match="User user_id 999 was not found"):
            token_db.delete(999)

    def test_delete_removes_record(self, monkeypatch, db_config):
        """Test that delete removes the record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "User1", "access_token": b"t1", "access_secret": b"s1"}
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        result = token_db.delete(1)

        assert result.user_id == 1
        mock_db.execute_query_safe.assert_called_with(
            "DELETE FROM user_tokens WHERE user_id = %s",
            (1,),
        )

    def test_add_delegates_to_upsert(self, monkeypatch, db_config):
        """Test that add method delegates to upsert."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "TestUser", "access_token": b"t1", "access_secret": b"s1"}
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_user_tokens.Database", lambda db_data: mock_db)

        with patch.object(UserTokenDB, "upsert") as mock_upsert:
            mock_upsert.return_value = UserTokenRecord(
                user_id=1, username="TestUser", access_token=b"t", access_secret=b"s"
            )

            token_db = UserTokenDB(db_config)
            result = token_db.add(1, "TestUser", "token", "secret")

            mock_upsert.assert_called_once_with(1, "TestUser", "token", "secret")
