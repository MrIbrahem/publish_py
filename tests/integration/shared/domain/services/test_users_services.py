"""
Integration tests for user_token_service module.
"""

from src.sqlalchemy_app.shared.domain.services.user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


class TestUserServiceIntegration:
    """Integration tests for user token service."""

    def test_full_token_lifecycle(self):
        """Test complete CRUD lifecycle through service layer."""
        upsert_user_token(
            user_id=12345,
            username="TestUser",
            access_key="test_key",
            access_secret="test_secret",
        )

        result = get_user_token(12345)
        assert result is not None
        assert result.user_id == 12345

        delete_user_token(12345)

        result = get_user_token(12345)
        assert result is None

    def test_username_lookup_integration(self):
        """Test username-based operations integrate correctly."""
        upsert_user_token(
            user_id=12345,
            username="TestUser",
            access_key="test_key",
            access_secret="test_secret",
        )

        result = get_user_token_by_username("TestUser")
        assert result is not None
        assert result.user_id == 12345

    def test_empty_username_handling(self):
        """Test service handles empty usernames gracefully."""
        result = get_user_token_by_username("")
        assert result is None

        result = delete_user_token_by_username("   ")
        assert result is None

    def test_lookup_error_handling(self):
        """Test service handles LookupError from DB layer."""
        result = get_user_token(99999)
        assert result is None

        result = get_user_token_by_username("NonExistent")
        assert result is None
