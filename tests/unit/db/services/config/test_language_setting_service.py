import pytest

from src.main_app.db.models import LanguageSettingRecord
from src.main_app.db.services.config import LanguageSettingService


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = LanguageSettingService()


class TestLanguageSettingService(TestSetup):
    """Tests for LanguageSettingService class."""

    def test_language_setting_workflow(self):
        service = LanguageSettingService()
        # Test add
        ls = service.add_language_setting("ar", 1, 0, 1)
        assert ls.lang_code == "ar"
        assert ls.move_dots == 1

        # Test get
        ls2 = service.get_language_setting(ls.id)
        assert ls2 is not None
        assert ls2.lang_code == "ar"

        # Test get by code
        ls3 = service.get_language_setting_by_code("ar")
        assert ls3 is not None
        assert ls3.id == ls.id

        # Test list
        all_ls = service.list_language_settings()
        assert any(x.lang_code == "ar" for x in all_ls)

        # Test update
        updated = service.update_language_setting(ls.id, move_dots=0)
        assert updated.move_dots == 0

        # Test add_or_update
        ls4 = service.add_or_update_language_setting("en", 1, 1, 1)
        assert ls4.move_dots == 1
        assert ls4.expend == 1

        # Test delete
        deleted = service.delete(ls.id)
        assert deleted is True
        assert service.get_language_setting(ls.id) is None

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_language_settings returns all records."""
        service = LanguageSettingService()
        service.add_language_setting("es")
        service.add_language_setting("fr")
        result = service.list_language_settings()
        assert len(result) >= 2


class TestGetLanguageSetting(TestSetup):
    """Tests for get_language_setting function."""

    def test_returns_setting_record(self, monkeypatch):
        """Test that function returns a LanguageSettingRecord."""
        service = LanguageSettingService()
        ls = service.add_language_setting("zh")
        result = service.get_language_setting(ls.id)
        assert isinstance(result, LanguageSettingRecord)
        assert result.lang_code == "zh"

    def test_returns_none_when_not_found(self, monkeypatch):
        service = LanguageSettingService()
        assert service.get_language_setting(9999) is None


class TestGetLanguageSettingByCode(TestSetup):
    """Tests for get_language_setting_by_code function."""

    def test_returns_setting_by_lang_code(self, monkeypatch):
        """Test that function returns setting by language code."""
        service = LanguageSettingService()
        service.add_language_setting("hi")
        result = service.get_language_setting_by_code("hi")
        assert result is not None
        assert result.lang_code == "hi"

    def test_returns_none_when_not_found(self, monkeypatch):
        service = LanguageSettingService()
        assert service.get_language_setting_by_code("ghost") is None


class TestAddLanguageSetting(TestSetup):
    """Tests for add_language_setting function."""

    def test_adds_setting_and_returns_record(self, monkeypatch):
        """Test that add_language_setting adds and returns the record."""
        service = LanguageSettingService()
        record = service.add_language_setting("pt")
        assert record.lang_code == "pt"

    def test_raises_error_if_exists(self, monkeypatch):
        service = LanguageSettingService()
        service.add_language_setting("en")
        with pytest.raises(ValueError, match="already exists"):
            service.add_language_setting("en")

    def test_raises_error_if_no_code(self, monkeypatch):
        service = LanguageSettingService()
        with pytest.raises(ValueError, match="Language code is required"):
            service.add_language_setting("")


class TestAddOrUpdateLanguageSetting(TestSetup):
    """Tests for add_or_update_language_setting function."""

    def test_upserts_setting(self, monkeypatch):
        """Test that add_or_update_language_setting upserts the record."""
        service = LanguageSettingService()
        service.add_language_setting("ru", move_dots=0)
        record = service.add_or_update_language_setting("ru", move_dots=1)
        assert record.move_dots == 1
        assert len(service.list_language_settings()) == 1

    def test_raises_error_if_no_code(self, monkeypatch):
        service = LanguageSettingService()
        with pytest.raises(ValueError, match="Language code is required"):
            service.add_or_update_language_setting(" ")


class TestUpdateLanguageSetting(TestSetup):
    """Tests for update_language_setting function."""

    def test_updates_setting_and_returns_record(self, monkeypatch):
        """Test that update_language_setting updates and returns the record."""
        service = LanguageSettingService()
        ls = service.add_language_setting("ja", move_dots=1)
        updated = service.update_language_setting(ls.id, move_dots=0)
        assert updated.move_dots == 0

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        service = LanguageSettingService()
        ls = service.add_language_setting("ko")
        result = service.update_language_setting(ls.id)
        assert result.lang_code == "ko"

    def test_raises_error_if_not_found(self, monkeypatch):
        service = LanguageSettingService()
        with pytest.raises(ValueError, match="not found"):
            service.update_language_setting(9999, move_dots=1)


class TestDeleteLanguageSetting(TestSetup):
    """Tests for delete function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete calls store delete."""
        service = LanguageSettingService()
        ls = service.add_language_setting("de")
        deleted = service.delete(ls.id)
        assert deleted is True
        assert service.get_language_setting(ls.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        service = LanguageSettingService()
        assert service.delete(9999) is False
