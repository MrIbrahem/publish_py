from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.models import _LangRecord
from src.sqlalchemy_app.public.services.lang_service import (
    add_lang,
    add_or_update_lang,
    delete_lang,
    get_lang,
    get_lang_by_code,
    list_langs,
    update_lang,
)
from src.sqlalchemy_app.shared.db_models.public_models import LangRecord


def test_lang_workflow():
    # Test add
    l = add_lang("ar", "العربية", "Arabic")
    assert l.code == "ar"
    assert l.autonym == "العربية"

    # Test get
    l2 = get_lang(l.lang_id)
    assert l2.code == "ar"

    # Test get by code
    l3 = get_lang_by_code("ar")
    assert l3.lang_id == l.lang_id

    # Test list
    all_l = list_langs()
    assert any(x.code == "ar" for x in all_l)

    # Test update
    updated = update_lang(l.lang_id, autonym="Arabe")
    assert updated.autonym == "Arabe"

    # Test add_or_update
    l4 = add_or_update_lang("ar", "العربية", "Modern Standard Arabic")
    assert l4.name == "Modern Standard Arabic"

    # Test delete
    delete_lang(l.lang_id)
    assert get_lang(l.lang_id) is None


class TestListLangs:
    """Tests for list_langs function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_lang("en", "English", "English")
        add_lang("fr", "Français", "French")
        result = list_langs()
        assert len(result) >= 2


class TestGetLang:
    """Tests for get_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        l = add_lang("es", "Español", "Spanish")
        result = get_lang(l.lang_id)
        assert isinstance(result, LangRecord)
        assert result.code == "es"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_lang(9999) is None


class TestGetLangByCode:
    """Tests for get_lang_by_code function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by code."""
        add_lang("de", "Deutsch", "German")
        result = get_lang_by_code("de")
        assert result.code == "de"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_lang_by_code("ghost") is None


class TestAddLang:
    """Tests for add_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_lang("it", "Italiano", "Italian")
        assert record.code == "it"

    def test_raises_error_if_exists(self, monkeypatch):
        # Lang table in models.py doesn't have UNIQUE on code.
        # But service expects it.
        from sqlalchemy.exc import IntegrityError

        with patch("src.sqlalchemy_app.public.services.lang_service.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_session.commit.side_effect = IntegrityError(None, None, None)
            mock_get_session.return_value.__enter__.return_value = mock_session
            with pytest.raises(ValueError, match="already exists"):
                add_lang("en", "En", "En")

    def test_raises_error_if_no_code(self, monkeypatch):
        with pytest.raises(ValueError, match="Language code is required"):
            add_lang("", "Autonym", "Name")


class TestAddOrUpdateLang:
    """Tests for add_or_update_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_lang("pt", "Português", "Portuguese")
        record = add_or_update_lang("pt", "Português", "Portuguese (Brazil)")
        assert record.name == "Portuguese (Brazil)"
        assert len(list_langs()) == 1

    def test_raises_error_if_no_code(self, monkeypatch):
        with pytest.raises(ValueError, match="Language code is required"):
            add_or_update_lang(" ", "A", "N")


class TestUpdateLang:
    """Tests for update_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        l = add_lang("hi", "हिन्दी", "Hindi")
        updated = update_lang(l.lang_id, autonym="Hindi Autonym")
        assert updated.autonym == "Hindi Autonym"

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        l = add_lang("ja", "J", "J")
        result = update_lang(l.lang_id)
        assert result.code == "ja"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_lang(9999, autonym="Ar")


class TestDeleteLang:
    """Tests for delete_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        l = add_lang("ru", "Русский", "Russian")
        delete_lang(l.lang_id)
        assert get_lang(l.lang_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_lang(9999)
