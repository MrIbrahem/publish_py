from unittest.mock import patch

import pytest

from src.main_app.db.models import UserRecord
from src.main_app.db.services.users.user_service import (
    add_user,
    delete_user,
    get_user,
    get_user_by_username,
    list_users,
    list_users_by_group,
    update_user,
    update_user_data,
    user_exists,
)
from src.main_app.shared.core.extensions import db

pytestmark = pytest.mark.unit


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

    deleted = delete_user(u.user_id)
    assert deleted is True
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

        with patch.object(db.session, "commit", side_effect=IntegrityError(None, None, None)):
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


class TestUpdateUserFull:
    """Tests for the update_user function (full field replacement, added to __all__ in this PR)."""

    def test_updates_all_fields(self, monkeypatch):
        """update_user replaces all user fields and returns the updated record."""
        u = add_user("Original_Name", email="old@example.com", wiki="enwiki", user_group="Editor")
        updated = update_user(u.user_id, username="New_Name", email="new@example.com", wiki="frwiki", user_group="Admin")

        assert updated.username == "New_Name"
        assert updated.email == "new@example.com"
        assert updated.wiki == "frwiki"
        assert updated.user_group == "Admin"

    def test_update_persists_to_db(self, monkeypatch):
        """Changes made by update_user are persisted and retrievable."""
        u = add_user("Persist_Test", email="before@example.com")
        update_user(u.user_id, username="Persist_Test", email="after@example.com")

        fetched = get_user(u.user_id)
        assert fetched.email == "after@example.com"

    def test_raises_on_nonexistent_user(self, monkeypatch):
        """Raises ValueError when user_id does not exist."""
        with pytest.raises(ValueError, match="not found"):
            update_user(99999, username="Ghost")

    def test_raises_on_empty_username(self, monkeypatch):
        """Raises ValueError when new username is empty or whitespace."""
        u = add_user("Valid_User")
        with pytest.raises(ValueError, match="Username is required"):
            update_user(u.user_id, username="   ")

    def test_strips_whitespace_from_username(self, monkeypatch):
        """Strips leading/trailing whitespace from username."""
        u = add_user("Whitespace_User")
        updated = update_user(u.user_id, username="  Trimmed  ")
        assert updated.username == "Trimmed"

    def test_returns_user_record_instance(self, monkeypatch):
        """update_user returns a UserRecord instance."""
        u = add_user("Return_Type_Check")
        result = update_user(u.user_id, username="Return_Type_Check")
        assert isinstance(result, UserRecord)

    def test_update_user_in_users_package(self, monkeypatch):
        """update_user is accessible via the users package __init__.py."""
        from src.main_app.db.services.users import update_user as pkg_update_user
        assert callable(pkg_update_user)

    def test_update_user_in_user_service_all(self):
        """update_user is listed in user_service.__all__."""
        from src.main_app.db.services.users import user_service
        assert "update_user" in user_service.__all__


class TestDeleteUser:
    """Tests for delete_user function."""


        """Test that function deletes the record."""
        u = add_user("Temporary_Account")
        deleted = delete_user(u.user_id)
        assert deleted is True
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
