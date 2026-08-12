import pytest

from src.main_app.database.models import FullTranslatorRecord
from src.main_app.database.services.users.full_translator_service import FullTranslatorService
from src.main_app.db.exceptions import RecordNotFoundError


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = FullTranslatorService()


class TestFullTranslatorService(TestSetup):
    """Tests for FullTranslatorService class."""

    def test_full_translator_workflow(self):
        # Test add
        ft = self.service.add_full_translator("Global_Translator", 1)
        assert ft.user == "Global_Translator"
        assert ft.is_active == 1

        # Test get
        ft2 = self.service.get_full_translator(ft.id)
        assert ft2 is not None
        assert ft2.user == "Global_Translator"

        # Test get by user
        ft3 = self.service.get_full_translator_by_user("Global_Translator")
        assert ft3 is not None
        assert ft3.id == ft.id

        # Test list
        all_ft = self.service.list_full_translators()
        assert any(x.user == "Global_Translator" for x in all_ft)

        # Test active
        active = self.service.list_active_full_translators()
        assert any(x.user == "Global_Translator" for x in active)

        # Test update
        updated = self.service.update_full_translator(ft.id, is_active=0)
        assert updated.is_active == 0
        assert self.service.is_full_translator("Global_Translator") is False

        # Test add_or_update
        ft4 = self.service.add_or_update_full_translator("Global_Translator", 1)
        assert ft4.is_active == 1
        assert self.service.is_full_translator("Global_Translator") is True

        # Test delete
        deleted = self.service.delete(ft.id)
        assert deleted is True
        assert self.service.get_full_translator(ft.id) is None

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_full_translators returns all records."""
        self.service.add_full_translator("Translator_Alpha")
        self.service.add_full_translator("Translator_Beta")
        result = self.service.list_full_translators()
        assert len(result) >= 2


class TestListActiveFullTranslators(TestSetup):
    """Tests for list_active_full_translators method."""

    def test_returns_active_records(self, monkeypatch):
        """Test that list_active_full_translators returns active records."""
        self.service.add_full_translator("Active_Trans", is_active=1)
        self.service.add_full_translator("Inactive_Trans", is_active=0)
        active = self.service.list_active_full_translators()
        assert len(active) == 1
        assert active[0].user == "Active_Trans"


class TestGetFullTranslator(TestSetup):
    """Tests for get_full_translator method."""

    def test_returns_translator_record(self, monkeypatch):
        """Test that method returns a FullTranslatorRecord."""
        ft = self.service.add_full_translator("Expert_Linguist")
        result = self.service.get_full_translator(ft.id)
        assert isinstance(result, FullTranslatorRecord)
        assert result.user == "Expert_Linguist"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_full_translator(9999) is None


class TestGetFullTranslatorByUser(TestSetup):
    """Tests for get_full_translator_by_user method."""

    def test_returns_translator_by_user(self, monkeypatch):
        """Test that method returns translator by username."""
        self.service.add_full_translator("Polyglot_Wiki")
        result = self.service.get_full_translator_by_user("Polyglot_Wiki")
        assert result is not None
        assert result.user == "Polyglot_Wiki"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_full_translator_by_user("Ghost") is None


class TestAddFullTranslator(TestSetup):
    """Tests for add_full_translator method."""

    def test_adds_translator_and_returns_record(self, monkeypatch):
        """Test that add_full_translator adds and returns the record."""
        record = self.service.add_full_translator("New_Translator")
        assert record.user == "New_Translator"

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_full_translator("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            self.service.add_full_translator("Duplicate")

    def test_raises_error_if_no_user(self, monkeypatch):
        with pytest.raises(ValueError, match="User is required"):
            self.service.add_full_translator("")


class TestAddOrUpdateFullTranslator(TestSetup):
    """Tests for add_or_update_full_translator method."""

    def test_upserts_translator(self, monkeypatch):
        """Test that add_or_update_full_translator upserts the record."""
        self.service.add_full_translator("Sync_Trans", is_active=1)
        record = self.service.add_or_update_full_translator("Sync_Trans", is_active=0)
        assert record.is_active == 0
        assert len(self.service.list_full_translators()) == 1

    def test_raises_error_if_no_user(self, monkeypatch):
        with pytest.raises(ValueError, match="User is required"):
            self.service.add_or_update_full_translator(" ")


class TestUpdateFullTranslator(TestSetup):
    """Tests for update_full_translator method."""

    def test_updates_translator_and_returns_record(self, monkeypatch):
        """Test that update_full_translator updates and returns the record."""
        ft = self.service.add_full_translator("Update_Trans", is_active=1)
        updated = self.service.update_full_translator(ft.id, is_active=0)
        assert updated.is_active == 0

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        ft = self.service.add_full_translator("No_Change")
        result = self.service.update_full_translator(ft.id)
        assert result.user == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_full_translator(9999, is_active=0)


class TestDeleteFullTranslator(TestSetup):
    """Tests for delete_full_translator method."""

    def test_deletes_translator(self, monkeypatch):
        """Test that delete method deletes the record."""
        ft = self.service.add_full_translator("Delete_Trans")
        deleted = self.service.delete(ft.id)
        assert deleted is True
        assert self.service.get_full_translator(ft.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False


class TestIsFullTranslator(TestSetup):
    """Tests for is_full_translator method."""

    def test_returns_true_when_user_is_active_translator(self, monkeypatch):
        """Test that is_full_translator returns True for active translator."""
        self.service.add_full_translator("Active_Polyglot", is_active=1)
        assert self.service.is_full_translator("Active_Polyglot") is True

    def test_returns_false_when_user_not_translator(self, monkeypatch):
        """Test that is_full_translator returns False when user not found."""
        assert self.service.is_full_translator("Ghost_User") is False

    def test_returns_false_when_translator_inactive(self, monkeypatch):
        """Test that is_full_translator returns False for inactive translator."""
        self.service.add_full_translator("Inactive_Polyglot", is_active=0)
        assert self.service.is_full_translator("Inactive_Polyglot") is False
