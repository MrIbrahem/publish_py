"""
Unit tests for domain/services/lang_service.py module.

Tests for langs service layer which provides cached access to LangsDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.lang_service import (
    add_lang,
    add_or_update_lang,
    delete_lang,
    get_lang,
    get_lang_by_code,
    get_langs_db,
    list_langs,
    update_lang,
)


class TestGetLangsDb:
    """Tests for get_langs_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service._LANGS_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.has_db_config", lambda: True)

        result = get_langs_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service._LANGS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="LangsDB requires database configuration"):
            get_langs_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new LangsDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service._LANGS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.lang_service.LangsDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_langs_db()

            assert result is mock_db_instance


class TestListLangs:
    """Tests for list_langs function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.get_langs_db", lambda: mock_store)

        result = list_langs()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestGetLang:
    """Tests for get_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.get_langs_db", lambda: mock_store)

        result = get_lang(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetLangByCode:
    """Tests for get_lang_by_code function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_code."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_code.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.get_langs_db", lambda: mock_store)

        result = get_lang_by_code("ar")

        assert result is mock_record
        mock_store.fetch_by_code.assert_called_once_with("ar")


class TestAddLang:
    """Tests for add_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.get_langs_db", lambda: mock_store)

        result = add_lang("ar", "العربية", "Arabic")

        assert result is mock_record
        mock_store.add.assert_called_once_with("ar", "العربية", "Arabic")


class TestAddOrUpdateLang:
    """Tests for add_or_update_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.get_langs_db", lambda: mock_store)

        result = add_or_update_lang("ar", "العربية", "Arabic")

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("ar", "العربية", "Arabic")


class TestUpdateLang:
    """Tests for update_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.get_langs_db", lambda: mock_store)

        result = update_lang(1, name="New Arabic")

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, name="New Arabic")


class TestDeleteLang:
    """Tests for delete_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr("src.app_main.public.domain.services.lang_service.get_langs_db", lambda: mock_store)

        result = delete_lang(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)
