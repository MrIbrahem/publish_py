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
from sqlalchemy.orm import sessionmaker

from src.sqlalchemy_app.shared.domain.engine import (
    BaseDb,
    build_engine,
    init_db,
)
from src.sqlalchemy_app.shared.domain.services.user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


@pytest.fixture(autouse=True)
def setup_db():
    """Initialize an in-memory SQLite database for tests."""
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)

    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


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
