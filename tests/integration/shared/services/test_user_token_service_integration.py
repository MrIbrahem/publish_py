"""
Integration tests for user_token_service module.
"""

from src.main_app.db.services.users.user_token_service import UserTokenService
from src.main_app.db.services.users.users_service import UsersService


class TestUserServiceIntegration:
    """Integration tests for user token service."""

    def setup_method(self):
        self.service = UserTokenService()
        self.user_service = UsersService()

    def test_full_token_lifecycle(self):
        """Test complete CRUD lifecycle through service layer."""
        user = self.user_service.create_user("TestUser")
        user_id = user.user_id
        self.service.upsert_user_token(
            user_id,
            b"test_key",
            b"test_secret",
        )

        result = self.service.get_user_token(user_id)
        assert result is not None
        assert result.user_id == user_id

        self.service.delete(user_id)

        result = self.service.get_user_token(user_id)
        assert result is None
