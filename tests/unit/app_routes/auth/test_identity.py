"""
Unit tests for auth module.

Tests for current user helpers.
"""

import pytest

from src.main_app.shared.auth.current_user import (
    CurrentUser,
)


class TestCurrentUser:
    """Tests for CurrentUser dataclass."""

    def test_create_with_fields(self):
        """Test creating CurrentUser with fields."""
        user = CurrentUser(
            user_id=12345,
            username="TestUser",
            access_token=b"token",
            access_secret=b"secret",
        )

        assert user.user_id == 12345
        assert user.username == "TestUser"
        assert user.access_token == b"token"
        assert user.access_secret == b"secret"

    def test_is_frozen(self):
        """Test that CurrentUser is immutable."""
        user = CurrentUser(
            user_id=12345,
            username="TestUser",
            access_token=b"token",
            access_secret=b"secret",
        )

        with pytest.raises(AttributeError):
            user.user_id = 99999 # type: ignore
