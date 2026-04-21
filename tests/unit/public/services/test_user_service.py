from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.db_models.public_models import UserRecord
from src.sqlalchemy_app.public.models import _UserRecord
from src.sqlalchemy_app.public.services.user_service import (
    add_user,
    delete_user,
    get_user,
    get_user_by_username,
    list_users,
    list_users_by_group,
    update_user_data,
    user_exists,
)


def test_user_workflow():
    u = add_user("Wiki_User", "jh@example.com", "enwiki", "Editor")
    assert u.username == "Wiki_User"

    assert get_user(u.user_id).username == "Wiki_User"
    assert get_user_by_username("Wiki_User").user_id == u.user_id

    assert any(x.username == "Wiki_User" for x in list_users())
    assert any(x.username == "Wiki_User" for x in list_users_by_group("Editor"))

    updated = update_user_data(u.user_id, email="jh_new@example.com")
    assert updated.email == "jh_new@example.com"

    assert user_exists("Wiki_User") is True

    delete_user(u.user_id)
    assert get_user(u.user_id) is None


class TestListUsers:
    """Tests for list_users function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_user("Wiki_Admin")
        add_user("Wiki_Editor")
        result = list_users()
        assert len(result) >= 2


class TestListUsersByGroup:
    """Tests for list_users_by_group function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns filtered list from store."""
        add_user("Expert1", user_group="Medical_Board")
        add_user("Expert2", user_group="General_Board")
        result = list_users_by_group("Medical_Board")
        assert len(result) == 1
        assert result[0].username == "Expert1"


class TestGetUser:
    """Tests for get_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        u = add_user("ContributorA")
        result = get_user(u.user_id)
        assert isinstance(result, UserRecord)
        assert result.username == "ContributorA"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_user(9999) is None


class TestGetUserByUsername:
    """Tests for get_user_by_username function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by username."""
        add_user("Linguist_Specialist")
        result = get_user_by_username("Linguist_Specialist")
        assert result.username == "Linguist_Specialist"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_user_by_username("Ghost") is None


class TestAddUser:
    """Tests for add_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_user("New_Researcher", "research@wiki.org", "enwiki", "Researcher")
        assert record.username == "New_Researcher"
        assert record.email == "research@wiki.org"

    def test_raises_error_if_exists(self, monkeypatch):
        # User table in models.py doesn't have UNIQUE on username.
        # But service expects it.
        from sqlalchemy.exc import IntegrityError

        with patch("src.sqlalchemy_app.public.services.user_service.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_session.commit.side_effect = IntegrityError(None, None, None)
            mock_get_session.return_value.__enter__.return_value = mock_session
            with pytest.raises(ValueError, match="already exists"):
                add_user("Duplicate")

    def test_raises_error_if_no_username(self, monkeypatch):
        with pytest.raises(ValueError, match="Username is required"):
            add_user("")


class TestUpdateUser:
    """Tests for update_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        u = add_user("Bureaucrat1", email="old_email")
        updated = update_user_data(u.user_id, email="new_email")
        assert updated.email == "new_email"

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        u = add_user("No_Change")
        result = update_user_data(u.user_id)
        assert result.username == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_user_data(9999, email="T")


class TestDeleteUser:
    """Tests for delete_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        u = add_user("Temporary_Account")
        delete_user(u.user_id)
        assert get_user(u.user_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_user(9999)


class TestUserExists:
    """Tests for user_exists function."""

    def test_returns_true_when_user_exists(self, monkeypatch):
        """Test that function returns True when user found."""
        add_user("Active_Member")
        assert user_exists("Active_Member") is True

    def test_returns_false_when_user_not_found(self, monkeypatch):
        """Test that function returns False when user not found."""
        assert user_exists("Nonexistent_Member") is False
