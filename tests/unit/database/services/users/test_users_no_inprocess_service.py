import pytest

from src.main_app.database.exceptions import RecordNotFoundError
from src.main_app.database.models import UsersNoInprocessRecord
from src.main_app.database.services.users import UsersNoInprocessService


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = UsersNoInprocessService()


class TestUsersNoInprocessService(TestSetup):
    """Tests for UsersNoInprocessService class."""

    def test_users_no_inprocess_workflow(self):
        # Test add
        rec = self.service.add_users_no_inprocess("User_1", 1)
        assert rec.user == "User_1"
        assert rec.is_active == 1

        # Test get
        rec2 = self.service.get_users_no_inprocess(rec.id)
        assert rec2 is not None
        assert rec2.user == "User_1"

        # Test get by user
        rec3 = self.service.get_users_no_inprocess_by_user("User_1")
        assert rec3 is not None
        assert rec3.id == rec.id

        # Test list
        all_rec = self.service.list_users_no_inprocess()
        assert any(x.user == "User_1" for x in all_rec)

        # Test is_active
        is_active = self.service.list_active_users_no_inprocess()
        assert any(x.user == "User_1" for x in is_active)

        # Test update
        updated = self.service.update_users_no_inprocess(rec.id, is_active=0)
        assert updated.is_active == 0
        assert self.service.should_hide_from_inprocess("User_1") is False

        # Test add_or_update
        rec4 = self.service.add_or_update_users_no_inprocess("User_1", 1)
        assert rec4.is_active == 1
        assert self.service.should_hide_from_inprocess("User_1") is True

        # Test delete
        deleted = self.service.delete(rec.id)
        assert deleted is True
        assert self.service.get_users_no_inprocess(rec.id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns all records."""
        self.service.add_users_no_inprocess("User_One")
        self.service.add_users_no_inprocess("User_Two")
        result = self.service.list_users_no_inprocess()
        assert len(result) >= 2


class TestListActiveUsersNoInprocess(TestSetup):
    """Tests for list_active_users_no_inprocess method."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns is_active records."""
        self.service.add_users_no_inprocess("Active_Wiki_User", is_active=1)
        self.service.add_users_no_inprocess("Inactive_Wiki_User", is_active=0)
        is_active = self.service.list_active_users_no_inprocess()
        assert len(is_active) == 1
        assert is_active[0].user == "Active_Wiki_User"


class TestGetUsersNoInprocess(TestSetup):
    """Tests for get_users_no_inprocess method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by ID."""
        rec = self.service.add_users_no_inprocess("Clinical_Editor")
        result = self.service.get_users_no_inprocess(rec.id)
        assert isinstance(result, UsersNoInprocessRecord)
        assert result.user == "Clinical_Editor"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_users_no_inprocess(9999) is None


class TestGetUsersNoInprocessByUser(TestSetup):
    """Tests for get_users_no_inprocess_by_user method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by username."""
        self.service.add_users_no_inprocess("Medical_Librarian")
        result = self.service.get_users_no_inprocess_by_user("Medical_Librarian")
        assert result is not None
        assert result.user == "Medical_Librarian"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_users_no_inprocess_by_user("Ghost") is None


class TestAddUsersNoInprocess(TestSetup):
    """Tests for add_users_no_inprocess method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method adds and returns the record."""
        record = self.service.add_users_no_inprocess("Science_Writer")
        assert record.user == "Science_Writer"

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_users_no_inprocess("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            self.service.add_users_no_inprocess("Duplicate")

    def test_raises_error_if_no_user(self, monkeypatch):
        with pytest.raises(ValueError, match="User is required"):
            self.service.add_users_no_inprocess("")


class TestAddOrUpdateUsersNoInprocess(TestSetup):
    """Tests for add_or_update_users_no_inprocess method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method upserts the record."""
        self.service.add_users_no_inprocess("Regular_Editor", is_active=1)
        record = self.service.add_or_update_users_no_inprocess("Regular_Editor", is_active=0)
        assert record.is_active == 0
        assert len(self.service.list_users_no_inprocess()) == 1

    def test_raises_error_if_no_user(self, monkeypatch):
        with pytest.raises(ValueError, match="User is required"):
            self.service.add_or_update_users_no_inprocess(" ")


class TestUpdateUsersNoInprocess(TestSetup):
    """Tests for update_users_no_inprocess method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method updates and returns the record."""
        rec = self.service.add_users_no_inprocess("Target_User", is_active=1)
        updated = self.service.update_users_no_inprocess(rec.id, is_active=0)
        assert updated.is_active == 0

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        rec = self.service.add_users_no_inprocess("No_Change")
        result = self.service.update_users_no_inprocess(rec.id)
        assert result.user == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_users_no_inprocess(9999, is_active=0)


class TestDeleteUsersNoInprocess(TestSetup):
    """Tests for delete_users_no_inprocess method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method deletes the record."""
        rec = self.service.add_users_no_inprocess("To_Delete")
        deleted = self.service.delete(rec.id)
        assert deleted is True
        assert self.service.get_users_no_inprocess(rec.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False


class TestShouldHideFromInprocess(TestSetup):
    """Tests for should_hide_from_inprocess method."""

    def test_returns_true_when_record_exists_and_active(self, monkeypatch):
        """Test that method returns True when record exists and is is_active."""
        self.service.add_users_no_inprocess("Quiet_Editor", is_active=1)
        assert self.service.should_hide_from_inprocess("Quiet_Editor") is True

    def test_returns_false_when_record_exists_but_inactive(self, monkeypatch):
        """Test that method returns False when record exists but is inactive."""
        self.service.add_users_no_inprocess("Noisy_Editor", is_active=0)
        assert self.service.should_hide_from_inprocess("Noisy_Editor") is False

    def test_returns_false_when_no_record(self, monkeypatch):
        """Test that method returns False when no record found."""
        assert self.service.should_hide_from_inprocess("Ghost_Account") is False
