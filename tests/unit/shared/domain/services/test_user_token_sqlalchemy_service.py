from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.shared.domain_models import UserTokenRecord
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db
from src.sqlalchemy_app.shared.domain.models import _UserTokenRecord
from src.sqlalchemy_app.shared.domain.services.user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_user_token_workflow():
    upsert_user_token(user_id=1, username="test_user", access_key="key", access_secret="secret")
    t = get_user_token(1)
    assert t.username == "test_user"
    assert get_user_token_by_username("test_user").user_id == 1
    delete_user_token_by_username("test_user")
    assert get_user_token(1) is None
    upsert_user_token(user_id=2, username="user2", access_key="k2", access_secret="s2")
    delete_user_token(2)
    assert get_user_token(2) is None


class TestUpsertUserToken:
    """Tests for upsert_user_token function."""

    def test_delegates_to_store_upsert(self, monkeypatch):
        """Test that function inserts a token."""
        upsert_user_token(user_id=1, username="u1", access_key="k1", access_secret="s1")
        record = get_user_token(1)
        assert record.username == "u1"


class TestGetUserToken:
    """Tests for get_user_token function."""

    def test_returns_none_for_empty_user_id(self):
        """Test that None is returned for empty user_id."""
        assert get_user_token(None) is None
        assert get_user_token("") is None

    def test_returns_record_when_found(self, monkeypatch):
        """Test that record is returned when found."""
        upsert_user_token(user_id=1, username="u1", access_key="k1", access_secret="s1")
        record = get_user_token(1)
        assert isinstance(record, UserTokenRecord)
        assert record.user_id == 1

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""
        assert get_user_token(999) is None


class TestDeleteUserToken:
    """Tests for delete_user_token function."""

    def test_returns_none_for_empty_user_id(self, monkeypatch):
        """Test that None is returned for empty user_id."""
        # Function returns None by default when empty user_id
        assert delete_user_token(None) is None

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function deletes the token."""
        upsert_user_token(user_id=1, username="u1", access_key="k1", access_secret="s1")
        delete_user_token(1)
        assert get_user_token(1) is None


class TestGetUserTokenByUsername:
    """Tests for get_user_token_by_username function."""

    def test_returns_none_for_empty_username(self):
        """Test that None is returned for empty username."""
        assert get_user_token_by_username("") is None
        assert get_user_token_by_username("   ") is None

    def test_strips_whitespace_from_username(self, monkeypatch):
        """Test that username is stripped of whitespace."""
        upsert_user_token(user_id=1, username="u1", access_key="k1", access_secret="s1")
        assert get_user_token_by_username("  u1  ").user_id == 1

    def test_returns_record_when_found(self, monkeypatch):
        """Test that record is returned when found."""
        upsert_user_token(user_id=1, username="u1", access_key="k1", access_secret="s1")
        assert get_user_token_by_username("u1").user_id == 1

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""
        assert get_user_token_by_username("ghost") is None


class TestDeleteUserTokenByUsername:
    """Tests for delete_user_token_by_username function."""

    def test_returns_none_for_empty_username(self, monkeypatch):
        """Test that None is returned for empty username."""
        assert delete_user_token_by_username("") is None

    def test_deletes_by_user_id_when_found(self, monkeypatch):
        """Test that token is deleted by user_id when username found."""
        upsert_user_token(user_id=1, username="u1", access_key="k1", access_secret="s1")
        delete_user_token_by_username("u1")
        assert get_user_token(1) is None

    def test_skips_delete_when_user_not_found(self, monkeypatch):
        """Test that delete is skipped when username not found."""
        # Should not raise error
        delete_user_token_by_username("non_existent")
