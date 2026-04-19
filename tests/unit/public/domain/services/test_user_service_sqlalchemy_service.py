from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain_models import UserRecord
from src.sqlalchemy_app.public.domain.models import _UserRecord
from src.sqlalchemy_app.public.domain.services.user_service import (
    add_or_update_user,
    add_user,
    delete_user,
    get_user,
    get_user_by_username,
    list_users,
    list_users_by_group,
    update_user,
    user_exists,
)
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db


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


def test_user_workflow():
    u = add_user("test_user", "test@example.com", "enwiki", "Editor")
    assert u.username == "test_user"
    assert get_user(u.user_id).username == "test_user"
    assert get_user_by_username("test_user").user_id == u.user_id
    assert any(x.username == "test_user" for x in list_users())
    assert any(x.username == "test_user" for x in list_users_by_group("Editor"))
    updated = update_user(u.user_id, email="new@example.com")
    assert updated.email == "new@example.com"
    assert user_exists("test_user") is True
    u4 = add_or_update_user("test_user", email="final@example.com")
    assert u4.email == "final@example.com"
    delete_user(u.user_id)
    assert get_user(u.user_id) is None


class TestListUsers:
    """Tests for list_users function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_user("u1")
        add_user("u2")
        result = list_users()
        assert len(result) >= 2


class TestListUsersByGroup:
    """Tests for list_users_by_group function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns filtered list from store."""
        add_user("u1", user_group="GroupA")
        add_user("u2", user_group="GroupB")
        result = list_users_by_group("GroupA")
        assert len(result) == 1
        assert result[0].username == "u1"


class TestGetUser:
    """Tests for get_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        u = add_user("u1")
        result = get_user(u.user_id)
        assert isinstance(result, UserRecord)
        assert result.username == "u1"


class TestGetUserByUsername:
    """Tests for get_user_by_username function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by username."""
        add_user("u1")
        result = get_user_by_username("u1")
        assert result.username == "u1"


class TestAddUser:
    """Tests for add_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_user("u1", "e1", "w1", "g1")
        assert record.username == "u1"
        assert record.email == "e1"


class TestAddOrUpdateUser:
    """Tests for add_or_update_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_user("u1", email="old@e.com")
        record = add_or_update_user("u1", email="new@e.com")
        assert record.email == "new@e.com"
        assert len(list_users()) == 1


class TestUpdateUser:
    """Tests for update_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        u = add_user("u1", email="old")
        updated = update_user(u.user_id, email="new")
        assert updated.email == "new"


class TestDeleteUser:
    """Tests for delete_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        u = add_user("u1")
        delete_user(u.user_id)
        assert get_user(u.user_id) is None


class TestUserExists:
    """Tests for user_exists function."""

    def test_returns_true_when_user_exists(self, monkeypatch):
        """Test that function returns True when user found."""
        add_user("u1")
        assert user_exists("u1") is True

    def test_returns_false_when_user_not_found(self, monkeypatch):
        """Test that function returns False when user not found."""
        assert user_exists("ghost") is False
