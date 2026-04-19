from unittest.mock import MagicMock, patch

import pytest
from src.db_models.shared_models import UserTokenRecord
from src.sqlalchemy_app.shared.domain.models import _UserTokenRecord
from src.sqlalchemy_app.shared.domain.services.user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


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
        """Test that function delegates to store.upsert."""
        ...


class TestGetUserToken:
    """Tests for get_user_token function."""

    def test_returns_none_for_empty_user_id(self):
        """Test that None is returned for empty user_id."""

    def test_returns_record_when_found(self, monkeypatch):
        """Test that record is returned when found."""

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""


class TestDeleteUserToken:
    """Tests for delete_user_token function."""

    def test_returns_none_for_empty_user_id(self, monkeypatch):
        """Test that None is returned for empty user_id."""

    def test_delegates_to_store_delete(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestGetUserTokenByUsername:
    """Tests for get_user_token_by_username function."""

    def test_returns_none_for_empty_username(self):
        """Test that None is returned for empty username."""

    def test_strips_whitespace_from_username(self, monkeypatch):
        """Test that username is stripped of whitespace."""

    def test_returns_record_when_found(self, monkeypatch):
        """Test that record is returned when found."""

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when user not found."""


class TestDeleteUserTokenByUsername:
    """Tests for delete_user_token_by_username function."""

    def test_returns_none_for_empty_username(self, monkeypatch):
        """Test that None is returned for empty username."""

    def test_deletes_by_user_id_when_found(self, monkeypatch):
        """Test that token is deleted by user_id when username found."""

    def test_skips_delete_when_user_not_found(self, monkeypatch):
        """Test that delete is skipped when username not found."""
