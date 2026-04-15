"""Unit tests for db.db_user_tokens module.

Tests for UserToken database operations.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.config import DbConfig
from src.new_app.shared.db.db_user_tokens import (
    UserTokenDB,
    UserTokenRecord,
    _coerce_bytes,
    current_ts,
)


@pytest.fixture
def db_config():
    """Fixture for DbConfig instance."""
    return DbConfig(
        db_name="test_db",
        db_host="localhost",
        db_user="user",
        db_password="pass",
    )


@pytest.fixture
def sample_token_record():
    """Fixture for a sample UserTokenRecord."""
    return UserTokenRecord(
        user_id=12345,
        username="TestUser",
        access_token=b"encrypted_token",
        access_secret=b"encrypted_secret",
        created_at="2024-01-01 00:00:00",
        updated_at="2024-01-01 00:00:00",
        last_used_at="2024-01-01 00:00:00",
        rotated_at=None,
    )


class TestCoerceBytes:
    """Tests for _coerce_bytes function."""

    def test_returns_bytes_unchanged(self):
        """Test that bytes input is returned unchanged."""
        input_bytes = b"test_bytes"
        result = _coerce_bytes(input_bytes)
        assert result == input_bytes

    def test_converts_bytearray_to_bytes(self):
        """Test that bytearray is converted to bytes."""
        input_bytearray = bytearray(b"test_bytes")
        result = _coerce_bytes(input_bytearray)
        assert isinstance(result, bytes)
        assert result == b"test_bytes"

    def test_converts_memoryview_to_bytes(self):
        """Test that memoryview is converted to bytes."""
        input_memoryview = memoryview(b"test_bytes")
        result = _coerce_bytes(input_memoryview)
        assert isinstance(result, bytes)
        assert result == b"test_bytes"

    def test_raises_on_invalid_type(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError, match="Expected bytes-compatible value"):
            _coerce_bytes("string_not_allowed")


class TestCurrentTs:
    """Tests for current_ts function."""

    def test_returns_string_format(self):
        """Test that function returns correctly formatted timestamp string."""
        result = current_ts()
        # Should be in format "YYYY-MM-DD HH:MM:SS"
        assert isinstance(result, str)
        assert len(result) == 19
        assert result[4] == "-"
        assert result[7] == "-"
        assert result[10] == " "
        assert result[13] == ":"
        assert result[16] == ":"

    def test_returns_utc_time(self):
        """Test that function returns UTC timestamp."""
        from datetime import datetime, timezone

        result = current_ts()
        # Parse the result
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        now_utc = datetime.now(timezone.utc)

        # Should be close to current UTC time (within same minute)
        assert abs((now_utc.replace(tzinfo=None) - parsed).total_seconds()) < 60


class TestUserTokenRecord:
    """Tests for UserTokenRecord dataclass."""

    def test_post_init_coerces_bytes(self):
        """Test that __post_init__ coerces access fields to bytes."""
        record = UserTokenRecord(
            user_id=1,
            username="Test",
            access_token=bytearray(b"token"),
            access_secret=memoryview(b"secret"),
        )
        assert isinstance(record.access_token, bytes)
        assert isinstance(record.access_secret, bytes)

    @patch("src.new_app.shared.db.db_user_tokens.decrypt_value")
    def test_decrypted_returns_tuple(self, mock_decrypt, sample_token_record):
        """Test that decrypted returns tuple of decrypted values."""
        mock_decrypt.side_effect = ["decrypted_token", "decrypted_secret"]

        result = sample_token_record.decrypted()

        assert result == ("decrypted_token", "decrypted_secret")
        assert mock_decrypt.call_count == 2


class TestUserTokenDB:
    """Tests for UserTokenDB class."""

    def test_init_creates_database(self, monkeypatch, db_config):
        """Test that initialization creates a Database instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)

        assert token_db.db is mock_db
        mock_db.execute_query_safe.assert_called_once()

    def test_get_user_id_returns_id_when_found(self, monkeypatch, db_config):
        """Test that get_user_id returns user_id when username found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"user_id": 12345}]

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

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

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        result = token_db.get_user_id("MissingUser")

        assert result is None

    def test_fetch_by_id_raises_lookup_error_when_not_found(self, monkeypatch, db_config):
        """Test that _fetch_by_id raises LookupError when user not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        with pytest.raises(LookupError, match="User user_id 999 was not found"):
            token_db._fetch_by_id(999)

    def test_fetch_by_username_raises_lookup_error_when_not_found(self, monkeypatch, db_config):
        """Test that _fetch_by_username raises LookupError when user not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        with pytest.raises(LookupError, match="User 'MissingUser' was not found"):
            token_db._fetch_by_username("MissingUser")

    def test_list_returns_all_records(self, monkeypatch, db_config):
        """Test that list returns all user token records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "User1", "access_token": b"t1", "access_secret": b"s1"},
            {"user_id": 2, "username": "User2", "access_token": b"t2", "access_secret": b"s2"},
        ]

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        result = token_db.list()

        assert len(result) == 2
        assert all(isinstance(r, UserTokenRecord) for r in result)
        assert result[0].user_id == 1
        assert result[1].user_id == 2

    def test_update_with_unknown_columns_raises_error(self, monkeypatch, db_config):
        """Test that update raises error for unknown columns."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "User1", "access_token": b"t1", "access_secret": b"s1"}
        ]

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        with pytest.raises(ValueError, match="Unknown or immutable columns for user_tokens"):
            token_db.update(1, unknown_column="value")

    @patch("src.new_app.shared.db.db_user_tokens.encrypt_value")
    def test_update_encrypts_token_columns(self, mock_encrypt, monkeypatch, db_config):
        """Test that update encrypts access_token and access_secret columns."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "User1", "access_token": b"t1", "access_secret": b"s1"}
        ]
        mock_encrypt.return_value = b"encrypted_value"

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        token_db.update(1, access_token="new_token")

        mock_encrypt.assert_called_with("new_token")
        # Check that encrypted value was passed to execute_query_safe
        call_args = mock_db.execute_query_safe.call_args
        assert b"encrypted_value" in call_args[0][1]

    def test_upsert_requires_non_empty_username(self, monkeypatch, db_config):
        """Test that upsert requires non-empty username."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        with pytest.raises(ValueError, match="Username is required"):
            token_db.upsert(1, "", "token", "secret")

        with pytest.raises(ValueError, match="Username is required"):
            token_db.upsert(1, "   ", "token", "secret")

    @patch("src.new_app.shared.db.db_user_tokens.encrypt_value")
    @patch("src.new_app.shared.db.db_user_tokens.current_ts")
    def test_upsert_executes_insert_query(self, mock_ts, mock_encrypt, monkeypatch, db_config):
        """Test that upsert executes correct INSERT query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "TestUser", "access_token": b"enc_token", "access_secret": b"enc_secret"}
        ]
        mock_ts.return_value = "2024-01-01 00:00:00"
        mock_encrypt.side_effect = [b"enc_token", b"enc_secret"]

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

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

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        token_db = UserTokenDB(db_config)
        with pytest.raises(LookupError, match="User user_id 999 was not found"):
            token_db.delete(999)

    def test_delete_removes_record(self, monkeypatch, db_config):
        """Test that delete removes the record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"user_id": 1, "username": "User1", "access_token": b"t1", "access_secret": b"s1"}
        ]

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

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

        monkeypatch.setattr("src.new_app.shared.db.db_user_tokens.Database", lambda db_data: mock_db)

        with patch.object(UserTokenDB, "upsert") as mock_upsert:
            mock_upsert.return_value = UserTokenRecord(
                user_id=1, username="TestUser", access_token=b"t", access_secret=b"s"
            )

            token_db = UserTokenDB(db_config)
            result = token_db.add(1, "TestUser", "token", "secret")

            mock_upsert.assert_called_once_with(1, "TestUser", "token", "secret")
