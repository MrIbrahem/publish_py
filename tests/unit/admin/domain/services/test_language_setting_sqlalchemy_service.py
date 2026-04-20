from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.admin.domain.models import _LanguageSettingRecord
from src.sqlalchemy_app.admin.domain.services.language_setting_service import (
    add_language_setting,
    add_or_update_language_setting,
    delete_language_setting,
    get_language_setting,
    get_language_setting_by_code,
    list_language_settings,
    update_language_setting,
)
from src.sqlalchemy_app.admin.domain_models import LanguageSettingRecord
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


def test_language_setting_workflow():
    # Test add
    ls = add_language_setting("ar", 1, 0, 1)
    assert ls.lang_code == "ar"
    assert ls.move_dots == 1

    # Test get
    ls2 = get_language_setting(ls.id)
    assert ls2.lang_code == "ar"

    # Test get by code
    ls3 = get_language_setting_by_code("ar")
    assert ls3.id == ls.id

    # Test list
    all_ls = list_language_settings()
    assert any(x.lang_code == "ar" for x in all_ls)

    # Test update
    updated = update_language_setting(ls.id, move_dots=0)
    assert updated.move_dots == 0

    # Test add_or_update
    ls4 = add_or_update_language_setting("ar", 1, 1, 1)
    assert ls4.move_dots == 1
    assert ls4.expend == 1

    # Test delete
    delete_language_setting(ls.id)
    assert get_language_setting(ls.id) is None


class TestListLanguageSettings:
    """Tests for list_language_settings function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_language_settings returns all records."""
        add_language_setting("es")
        add_language_setting("fr")
        result = list_language_settings()
        assert len(result) >= 2


class TestGetLanguageSetting:
    """Tests for get_language_setting function."""

    def test_returns_setting_record(self, monkeypatch):
        """Test that function returns a LanguageSettingRecord."""
        ls = add_language_setting("zh")
        result = get_language_setting(ls.id)
        assert isinstance(result, LanguageSettingRecord)
        assert result.lang_code == "zh"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_language_setting(9999) is None


class TestGetLanguageSettingByCode:
    """Tests for get_language_setting_by_code function."""

    def test_returns_setting_by_lang_code(self, monkeypatch):
        """Test that function returns setting by language code."""
        add_language_setting("hi")
        result = get_language_setting_by_code("hi")
        assert result.lang_code == "hi"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_language_setting_by_code("ghost") is None


class TestAddLanguageSetting:
    """Tests for add_language_setting function."""

    def test_adds_setting_and_returns_record(self, monkeypatch):
        """Test that add_language_setting adds and returns the record."""
        record = add_language_setting("pt")
        assert record.lang_code == "pt"

    def test_raises_error_if_exists(self, monkeypatch):
        add_language_setting("en")
        with pytest.raises(ValueError, match="already exists"):
            add_language_setting("en")

    def test_raises_error_if_no_code(self, monkeypatch):
        with pytest.raises(ValueError, match="Language code is required"):
            add_language_setting("")


class TestAddOrUpdateLanguageSetting:
    """Tests for add_or_update_language_setting function."""

    def test_upserts_setting(self, monkeypatch):
        """Test that add_or_update_language_setting upserts the record."""
        add_language_setting("ru", move_dots=0)
        record = add_or_update_language_setting("ru", move_dots=1)
        assert record.move_dots == 1
        assert len(list_language_settings()) == 1

    def test_raises_error_if_no_code(self, monkeypatch):
        with pytest.raises(ValueError, match="Language code is required"):
            add_or_update_language_setting(" ")


class TestUpdateLanguageSetting:
    """Tests for update_language_setting function."""

    def test_updates_setting_and_returns_record(self, monkeypatch):
        """Test that update_language_setting updates and returns the record."""
        ls = add_language_setting("ja", move_dots=1)
        updated = update_language_setting(ls.id, move_dots=0)
        assert updated.move_dots == 0

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        ls = add_language_setting("ko")
        result = update_language_setting(ls.id)
        assert result.lang_code == "ko"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_language_setting(9999, move_dots=1)


class TestDeleteLanguageSetting:
    """Tests for delete_language_setting function."""

    def test_deletes_setting(self, monkeypatch):
        """Test that delete_language_setting calls store delete."""
        ls = add_language_setting("de")
        delete_language_setting(ls.id)
        assert get_language_setting(ls.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_language_setting(9999)
