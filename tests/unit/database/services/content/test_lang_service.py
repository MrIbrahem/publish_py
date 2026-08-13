from unittest.mock import patch

import pytest

from src.main_app.database.models import LangRecord
from src.main_app.database.services.content.lang_service import LangService
from src.main_app.extensions import db

pytestmark = pytest.mark.unit


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = LangService()


class TestLangService(TestSetup):
    """Tests for LangService class."""

    def test_lang_workflow(self):
        # Test add
        added = self.service.add_lang("ar", "العربية", "Arabic")
        assert added.code == "ar"
        assert added.autonym == "العربية"

        # Test get
        l2 = self.service.get_lang(added.lang_id)
        assert l2 is not None
        assert l2.code == "ar"

        # Test get by code
        l3 = self.service.get_lang_by_code("ar")
        assert l3 is not None
        assert l3.lang_id == added.lang_id

        # Test list
        all_l = self.service.list_langs()
        assert any(x.code == "ar" for x in all_l)

        # Test add_or_update
        l4 = self.service.add_or_update_lang("ar", "العربية", "Modern Standard Arabic")
        assert l4.name == "Modern Standard Arabic"

        # Test delete
        deleted = self.service.delete(added.lang_id)
        assert deleted is True
        assert self.service.get_lang(added.lang_id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that method returns list from store."""
        self.service.add_lang("en", "English", "English")
        self.service.add_lang("fr", "Français", "French")
        result = self.service.list_langs()
        assert len(result) >= 2


class TestGetLang(TestSetup):
    """Tests for get_lang method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by ID."""
        added = self.service.add_lang("es", "Español", "Spanish")
        result = self.service.get_lang(added.lang_id)
        assert isinstance(result, LangRecord)
        assert result.code == "es"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_lang(9999) is None


class TestGetLangByCode(TestSetup):
    """Tests for get_lang_by_code method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by code."""
        self.service.add_lang("de", "Deutsch", "German")
        result = self.service.get_lang_by_code("de")
        assert result is not None
        assert result.code == "de"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_lang_by_code("ghost") is None


class TestAddLang(TestSetup):
    """Tests for add_lang method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method adds and returns record."""
        record = self.service.add_lang("it", "Italiano", "Italian")
        assert record.code == "it"

    def test_raises_error_if_exists(self, monkeypatch):
        from sqlalchemy.exc import IntegrityError

        with patch.object(db.session, "commit", side_effect=IntegrityError(None, None, None)):  # type: ignore
            with pytest.raises(ValueError, match="already exists"):
                self.service.add_lang("en", "En", "En")

    def test_raises_error_if_no_code(self, monkeypatch):
        with pytest.raises(ValueError, match="Language code is required"):
            self.service.add_lang("", "Autonym", "Name")

    def test_add_lang_with_redirects(self):
        """Test adding a new language with a list of redirects."""
        redirects = ["ara", "ar-SA"]
        record = self.service.add_lang("ar", "العربية", "Arabic", redirects=redirects)

        assert record.code == "ar"
        assert record.redirects == redirects
        assert isinstance(record.redirects, list)

    def test_add_lang_with_empty_redirects(self):
        """Test adding a language with an empty list for redirects."""
        record = self.service.add_lang("fr", "Français", "French", redirects=[])
        assert record.redirects == []


class TestAddOrUpdateLang(TestSetup):
    """Tests for add_or_update_lang method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method upserts record."""
        self.service.add_lang("pt", "Português", "Portuguese")
        record = self.service.add_or_update_lang("pt", "Português", "Portuguese (Brazil)")
        assert record.name == "Portuguese (Brazil)"
        assert len(self.service.list_langs()) == 1

    def test_raises_error_if_no_code(self, monkeypatch):
        with pytest.raises(ValueError, match="Language code is required"):
            self.service.add_or_update_lang(" ", "A", "N")

    def test_update_existing_redirects(self):
        """Test updating redirects for an existing language record."""
        self.service.add_lang("es", "Español", "Spanish", redirects=["spa"])

        new_redirects = ["spa", "es-ES", "es-MX"]
        record = self.service.add_or_update_lang("es", "Español", "Spanish", redirects=new_redirects)
        assert record is not None
        assert record.redirects == new_redirects

        assert isinstance(record.redirects, list)
        assert len(record.redirects) == 3

    def test_clear_redirects_on_update(self):
        """Test clearing redirects (setting to None) on an existing record."""
        self.service.add_lang("de", "Deutsch", "German", redirects=["ger", "deu"])

        record = self.service.add_or_update_lang("de", "Deutsch", "German", redirects=[])

        assert record.redirects == []

    def test_add_new_with_redirects_via_upsert(self):
        """Test that add_or_update_lang inserts redirects correctly for new records."""
        redirects = ["jpn"]
        record = self.service.add_or_update_lang("ja", "日本語", "Japanese", redirects=redirects)

        assert record.code == "ja"
        assert record.redirects == ["jpn"]


class TestDeleteLang(TestSetup):
    """Tests for delete_lang method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method deletes the record."""
        added = self.service.add_lang("ru", "Русский", "Russian")
        deleted = self.service.delete(added.lang_id)
        assert deleted is True
        assert self.service.get_lang(added.lang_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete(9999) is False
