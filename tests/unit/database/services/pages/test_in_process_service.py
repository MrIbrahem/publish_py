from unittest.mock import patch

import pytest

from src.main_app.database.models import InProcessRecord
from src.main_app.database.services.pages.in_process_service import (
    InProcessService,
)
from src.main_app.database.exceptions import RecordNotFoundError

pytestmark = pytest.mark.unit


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = InProcessService()


class TestInProcess(TestSetup):

    def test_in_process_workflow(self):
        # Test add
        ip = self.service.add_in_process(
            "World Health Organization", "Public_Health_Expert", "ar", "Medicine", "lead", 2500
        )
        assert ip.title == "World Health Organization"
        assert ip.user == "Public_Health_Expert"

        # Test get
        ip2 = self.service.get_in_process(ip.id)
        assert ip2 is not None
        assert ip2.title == "World Health Organization"

        # Test get by multiple keys
        ip3 = self.service.get_in_process_by_title_user_lang("World Health Organization", "Public_Health_Expert", "ar")
        assert ip3 is not None
        assert ip3.id == ip.id

        # Test list
        all_ip = self.service.list_in_process()
        assert any(x.title == "World Health Organization" for x in all_ip)

        # Test list by user/lang
        by_user = self.service.list_in_process_by_user("Public_Health_Expert")
        assert len(by_user) >= 1
        by_lang = self.service.list_in_process_by_lang("ar")
        assert len(by_lang) >= 1

        # Test self.service.is_in_process
        assert self.service.is_in_process("World Health Organization", "Public_Health_Expert", "ar") is True

        # Test update
        updated = self.service.update_in_process(ip.id, word=3000)
        assert updated.word == 3000

        # Test delete by title/user/lang
        success = InProcessService().delete_in_process_by_title_user_lang(
            "World Health Organization", "Public_Health_Expert", "ar"
        )
        assert success is True
        assert self.service.get_in_process(ip.id) is None

        # Test delete by ID
        ip_new = self.service.add_in_process("Common cold", "Medical_Student", "es")
        deleted = InProcessService().delete(ip_new.id)
        assert deleted is True
        assert self.service.get_in_process(ip_new.id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        self.service.add_in_process("Fever", "User_One", "en")
        self.service.add_in_process("Cough", "User_Two", "en")
        result = self.service.list_in_process()
        assert len(result) >= 2


class TestListInProcessByUser(TestSetup):
    """Tests for self.service.list_in_process_by_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by user."""
        self.service.add_in_process("Headache", "Brain_User", "en")
        self.service.add_in_process("Migraine", "Other_User", "en")
        result = self.service.list_in_process_by_user("Brain_User")
        assert len(result) == 1
        assert result[0].user == "Brain_User"


class TestListInProcessByLang(TestSetup):
    """Tests for self.service.list_in_process_by_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by language."""
        self.service.add_in_process("Back pain", "User_A", "en")
        self.service.add_in_process("Douleur dorsale", "User_A", "fr")
        result = self.service.list_in_process_by_lang("fr")
        assert len(result) == 1
        assert result[0].lang == "fr"


class TestGetInProcess(TestSetup):
    """Tests for self.service.get_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        ip = self.service.add_in_process("Sore throat", "User_B", "en")
        result = self.service.get_in_process(ip.id)
        assert isinstance(result, InProcessRecord)
        assert result.title == "Sore throat"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_in_process(9999) is None


class TestGetInProcessByTitleUserLang(TestSetup):
    """Tests for self.service.get_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title, user, and language."""
        self.service.add_in_process("Insomnia", "Sleepy_Editor", "en")
        result = self.service.get_in_process_by_title_user_lang("Insomnia", "Sleepy_Editor", "en")
        assert result is not None
        assert result.title == "Insomnia"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_in_process_by_title_user_lang("Ghost", "Ghost", "en") is None


class TestAddInProcess(TestSetup):
    """Tests for self.service.add_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = self.service.add_in_process("Nausea", "Stomach_Expert", "en", word=150)
        assert record.title == "Nausea"
        assert record.word == 150

    def test_raises_error_if_exists(self, sqlite_db):
        from sqlalchemy.exc import IntegrityError

        with patch.object(sqlite_db.session, "commit", side_effect=IntegrityError(None, None, None)):  # type: ignore
            with pytest.raises(ValueError, match="already exists"):
                self.service.add_in_process("Duplicate", "User", "en")

    def test_raises_error_if_missing_required(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_in_process("", "U", "L")
        with pytest.raises(ValueError, match="User is required"):
            self.service.add_in_process("T", "", "L")
        with pytest.raises(ValueError, match="Language is required"):
            self.service.add_in_process("T", "U", " ")


class TestUpdateInProcess(TestSetup):
    """Tests for self.service.update_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        ip = self.service.add_in_process("Rash", "Skin_Expert", "en", word=100)
        updated = self.service.update_in_process(ip.id, word=200)
        assert updated.word == 200

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        ip = self.service.add_in_process("No_Change", "U", "en")
        result = self.service.update_in_process(ip.id)
        assert result.title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_in_process(9999, word=10)


class TestDeleteInProcess(TestSetup):
    """Tests for delete_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        ip = self.service.add_in_process("Allergy", "Immune_Expert", "en")
        deleted = InProcessService().delete(ip.id)
        assert deleted is True
        assert self.service.get_in_process(ip.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert InProcessService().delete(9999) is False


class TestDeleteInProcessByTitleUserLang(TestSetup):
    """Tests for delete_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes by composite key."""
        self.service.add_in_process("Asthma", "Lung_Expert", "en")
        success = InProcessService().delete_in_process_by_title_user_lang("Asthma", "Lung_Expert", "en")
        assert success is True
        assert self.service.get_in_process_by_title_user_lang("Asthma", "Lung_Expert", "en") is None


class TestIsInProcess(TestSetup):
    """Tests for self.service.is_in_process function."""

    def test_returns_true_when_record_exists(self, monkeypatch):
        """Test that function returns True when record found."""
        self.service.add_in_process("Diabetes", "Endo_Expert", "en")
        assert self.service.is_in_process("Diabetes", "Endo_Expert", "en") is True

    def test_returns_false_when_record_not_found(self, monkeypatch):
        """Test that function returns False when record not found."""
        assert self.service.is_in_process("Ghost_Article", "Nonexistent_User", "en") is False
