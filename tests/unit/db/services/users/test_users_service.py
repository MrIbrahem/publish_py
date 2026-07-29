from unittest.mock import patch

import pytest

from src.main_app.db.models import UserRecord
from src.main_app.db.services.users.users_service import UsersService

pytestmark = pytest.mark.unit


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = UsersService()


class TestUsersService(TestSetup):
    """Tests for UsersService class."""

    def test_user_workflow(self):
        u = self.service.create_user("Wiki_User", email="jh@example.com", wiki="enwiki", user_group="Editor")
        assert u.username == "Wiki_User"

        _user = self.service.get_user(u.user_id)
        assert _user is not None
        assert _user.username == "Wiki_User"
        _by_name = self.service.get_user_by_username("Wiki_User")
        assert _by_name is not None
        assert _by_name.user_id == u.user_id

        assert any(x.username == "Wiki_User" for x in self.service.list_users())
        assert any(x.username == "Wiki_User" for x in self.service.list_users_by_group("Editor"))

        updated = self.service.update_user_data(u.user_id, email="jh_new@example.com")
        assert updated is not None
        assert updated.email == "jh_new@example.com"

        assert self.service.user_exists("Wiki_User") is True

        deleted = self.service.delete(u.user_id)
        assert deleted is True
        assert self.service.get_user(u.user_id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns list from store."""
        self.service.create_user("Wiki_Admin")
        self.service.create_user("Wiki_Editor")
        result = self.service.list_users()
        assert len(result) >= 2


class TestListUsersByGroup(TestSetup):
    """Tests for list_users_by_group method."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns filtered list from store."""
        self.service.create_user("Expert1", user_group="Medical_Board")
        self.service.create_user("Expert2", user_group="General_Board")
        result = self.service.list_users_by_group("Medical_Board")
        assert len(result) == 1
        assert result[0].username == "Expert1"


class TestGetUser(TestSetup):
    """Tests for get_user method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by ID."""
        u = self.service.create_user("ContributorA")
        result = self.service.get_user(u.user_id)
        assert isinstance(result, UserRecord)
        assert result.username == "ContributorA"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_user(9999) is None


class TestGetUserByUsername(TestSetup):
    """Tests for get_user_by_username method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by username."""
        self.service.create_user("Linguist_Specialist")
        result = self.service.get_user_by_username("Linguist_Specialist")
        assert result is not None
        assert result.username == "Linguist_Specialist"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_user_by_username("Ghost") is None


class TestAddUser(TestSetup):
    """Tests for create_user method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method adds and returns record."""
        record = self.service.create_user(
            "New_Researcher", email="research@wiki.org", wiki="enwiki", user_group="Researcher"
        )
        assert record.username == "New_Researcher"
        assert record.email == "research@wiki.org"

    def test_raises_error_if_exists(self, sqlite_db):
        from sqlalchemy.exc import IntegrityError

        with patch.object(
            sqlite_db.session,
            "commit",
            side_effect=IntegrityError(None, None, None),  # pyright: ignore[reportArgumentType]
        ):
            with pytest.raises(ValueError, match="already exists"):
                self.service.create_user("Duplicate")

    def test_raises_error_if_no_username(self, monkeypatch):
        with pytest.raises(ValueError, match="Username is required"):
            self.service.create_user("")


class TestUpdateUser(TestSetup):
    """Tests for update_user_data method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method updates and returns record."""
        u = self.service.create_user("Bureaucrat1", email="old_email")
        updated = self.service.update_user_data(u.user_id, email="new_email")
        assert updated is not None
        assert updated.email == "new_email"

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        u = self.service.create_user("No_Change")
        result = self.service.update_user_data(u.user_id)
        assert result is not None
        assert result.username == "No_Change"


class TestDeleteUser(TestSetup):
    """Tests for delete_user method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method deletes the record."""
        u = self.service.create_user("Temporary_Account")
        deleted = self.service.delete(u.user_id)
        assert deleted is True
        assert self.service.get_user(u.user_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False


class TestUserExists(TestSetup):
    """Tests for user_exists method."""

    def test_returns_true_when_user_exists(self, monkeypatch):
        """Test that method returns True when user found."""
        self.service.create_user("Active_Member")
        assert self.service.user_exists("Active_Member") is True

    def test_returns_false_when_user_not_found(self, monkeypatch):
        """Test that method returns False when user not found."""
        assert self.service.user_exists("Nonexistent_Member") is False
