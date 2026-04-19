"""
Unit tests for domain.models.user_token module.

Tests for UserTokenRecord.
"""

from unittest.mock import patch

import pytest
from src.db_models.shared_models import (
    UserTokenRecord,
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

    @patch("src.sqlalchemy_app.shared.core.crypto.decrypt_value")
    def test_decrypted_returns_tuple(self, mock_decrypt, sample_token_record):
        """Test that decrypted returns tuple of decrypted values."""
        mock_decrypt.side_effect = ["decrypted_token", "decrypted_secret"]

        result = sample_token_record.decrypted()

        assert result == ("decrypted_token", "decrypted_secret")
        assert mock_decrypt.call_count == 2
