"""
Integration tests for user_token_service module.
"""

from src.main_app.db.services.users import create_user
from src.main_app.db.services.users.user_token_service import (
    UserTokenService,
    get_user_token,
    upsert_user_token,
)


class TestUserServiceIntegration:
    """Integration tests for user token service."""

    def test_full_token_lifecycle(self):
        """Test complete CRUD lifecycle through service layer."""
        user = create_user("TestUser")
        user_id = user.user_id
        upsert_user_token(
            user_id,
            b"test_key",
            b"test_secret",
        )

        result = get_user_token(user_id)
        assert result is not None
        assert result.user_id == user_id

        UserTokenService().delete(user_id)

        result = get_user_token(user_id)
        assert result is None
