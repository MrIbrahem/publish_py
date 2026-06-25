"""
Integration tests for user_token_service module.
"""

from src.main_app.db.services.delete_service import (
    delete_user_token,
)
from src.main_app.db.services.users import create_user
from src.main_app.db.services.users.user_token_service import (
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


class TestUserServiceIntegration:
    """Integration tests for user token service."""

    def test_full_token_lifecycle(self):
        """Test complete CRUD lifecycle through service layer."""
        user = create_user("TestUser")
        user_id = user.user_id
        upsert_user_token(
            user_id=user_id,
            username="TestUser",
            access_key="test_key",
            access_secret="test_secret",
        )

        result = get_user_token(user_id)
        assert result is not None
        assert result.user_id == user_id

        delete_user_token(user_id)

        result = get_user_token(user_id)
        assert result is None

    def test_username_lookup_integration(self):
        """Test username-based operations integrate correctly."""
        user = create_user("TestUser")
        user_id = user.user_id
        upsert_user_token(
            user_id=user_id,
            access_key="test_key",
            access_secret="test_secret",
        )

        result = get_user_token_by_username("TestUser")
        assert result is not None
        assert result.user_id == user_id

    def test_lookup_error_handling(self):
        """Test service handles LookupError from DB layer."""
        result = get_user_token(99999)
        assert result is None

        result = get_user_token_by_username("NonExistent")
        assert result is None
