"""
Unit tests for domain/services/in_process_service.py module.

Tests for in_process service layer which provides cached access to InProcessDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.in_process_service import (
    add_in_process,
    delete_in_process,
    delete_in_process_by_title_user_lang,
    get_in_process,
    get_in_process_by_title_user_lang,
    get_in_process_db,
    is_in_process,
    list_in_process,
    list_in_process_by_lang,
    list_in_process_by_user,
    update_in_process,
)


class TestGetInProcessDb:
    """Tests for get_in_process_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.in_process_service._IN_PROCESS_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.in_process_service.has_db_config", lambda: True)

        result = get_in_process_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.in_process_service._IN_PROCESS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.in_process_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="InProcessDB requires database configuration"):
            get_in_process_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new InProcessDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.in_process_service._IN_PROCESS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.in_process_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.in_process_service.InProcessDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_in_process_db()

            assert result is mock_db_instance


class TestListInProcess:
    """Tests for list_in_process function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = list_in_process()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestListInProcessByUser:
    """Tests for list_in_process_by_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_by_user.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = list_in_process_by_user("TestUser")

        assert result is mock_records
        mock_store.list_by_user.assert_called_once_with("TestUser")


class TestListInProcessByLang:
    """Tests for list_in_process_by_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_records = [MagicMock()]
        mock_store.list_by_lang.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = list_in_process_by_lang("ar")

        assert result is mock_records
        mock_store.list_by_lang.assert_called_once_with("ar")


class TestGetInProcess:
    """Tests for get_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = get_in_process(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetInProcessByTitleUserLang:
    """Tests for get_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_title_user_lang.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = get_in_process_by_title_user_lang("TestPage", "TestUser", "ar")

        assert result is mock_record
        mock_store.fetch_by_title_user_lang.assert_called_once_with("TestPage", "TestUser", "ar")


class TestAddInProcess:
    """Tests for add_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = add_in_process("TestPage", "TestUser", "ar", cat="RTT", translate_type="lead", word=100)

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestPage", "TestUser", "ar", "RTT", "lead", 100)


class TestUpdateInProcess:
    """Tests for update_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = update_in_process(1, word=200)

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, word=200)


class TestDeleteInProcess:
    """Tests for delete_in_process function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = delete_in_process(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)


class TestDeleteInProcessByTitleUserLang:
    """Tests for delete_in_process_by_title_user_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_store.delete_by_title_user_lang.return_value = True
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = delete_in_process_by_title_user_lang("TestPage", "TestUser", "ar")

        assert result is True
        mock_store.delete_by_title_user_lang.assert_called_once_with("TestPage", "TestUser", "ar")


class TestIsInProcess:
    """Tests for is_in_process function."""

    def test_returns_true_when_record_exists(self, monkeypatch):
        """Test that function returns True when record found."""
        mock_store = MagicMock()
        mock_store.fetch_by_title_user_lang.return_value = MagicMock()
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = is_in_process("TestPage", "TestUser", "ar")

        assert result is True

    def test_returns_false_when_record_not_found(self, monkeypatch):
        """Test that function returns False when record not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_title_user_lang.return_value = None
        monkeypatch.setattr(
            "src.app_main.public.domain.services.in_process_service.get_in_process_db", lambda: mock_store
        )

        result = is_in_process("Missing", "TestUser", "ar")

        assert result is False
