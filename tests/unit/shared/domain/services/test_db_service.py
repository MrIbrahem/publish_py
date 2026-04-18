"""
Unit tests for domain/services/db_service.py module.

Tests for db_service compatibility functions.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.domain.db_service import (
    close_cached_db,
    execute_query,
    execute_query_safe,
    fetch_query,
    fetch_query_safe,
    get_db,
)


class TestGetDb:
    """Tests for get_db function."""

    def test_returns_cached_db_instance(self, monkeypatch):
        """Test that function returns cached instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.db_service._db", mock_db)

        result = get_db()

        assert result is mock_db

    def test_creates_new_instance_when_none(self, monkeypatch):
        """Test that function creates new instance when none cached."""
        monkeypatch.setattr("src.app_main.shared.domain.services.db_service._db", None)

        mock_db_instance = MagicMock()
        with patch("src.app_main.shared.domain.services.db_service.Database") as MockDatabase:
            MockDatabase.return_value = mock_db_instance

            result = get_db()

            assert result is mock_db_instance


class TestCloseCachedDb:
    """Tests for close_cached_db function."""

    def test_closes_and_clears_cached_db(self, monkeypatch):
        """Test that function closes and clears cached db."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.shared.domain.services.db_service._db", mock_db)

        close_cached_db()

        mock_db.close.assert_called_once()
        from src.app_main.shared.domain import db_service

        assert db_service._db is None

    def test_does_nothing_when_no_db_cached(self, monkeypatch):
        """Test that function does nothing when no db is cached."""
        monkeypatch.setattr("src.app_main.shared.domain.services.db_service._db", None)

        close_cached_db()

        from src.app_main.shared.domain import db_service

        assert db_service._db is None


class TestExecuteQuery:
    """Tests for execute_query function."""

    def test_delegates_to_db_execute_query(self, monkeypatch):
        """Test that function delegates to db.execute_query."""
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.execute_query.return_value = True
        monkeypatch.setattr("src.app_main.shared.domain.services.db_service._db", mock_db)

        result = execute_query("SELECT 1")

        assert result is True
        mock_db.execute_query.assert_called_once_with("SELECT 1", None)


class TestFetchQuery:
    """Tests for fetch_query function."""

    def test_delegates_to_db_fetch_query(self, monkeypatch):
        """Test that function delegates to db.fetch_query."""
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.fetch_query.return_value = [{"id": 1}]
        monkeypatch.setattr("src.app_main.shared.domain.services.db_service._db", mock_db)

        result = fetch_query("SELECT * FROM users")

        assert result == [{"id": 1}]
        mock_db.fetch_query.assert_called_once()


class TestExecuteQuerySafe:
    """Tests for execute_query_safe function."""

    def test_delegates_to_db_execute_query_safe(self, monkeypatch):
        """Test that function delegates to db.execute_query_safe."""
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.execute_query_safe.return_value = True
        monkeypatch.setattr("src.app_main.shared.domain.services.db_service._db", mock_db)

        result = execute_query_safe("INSERT INTO users VALUES (%s)", ("test",))

        assert result is True
        mock_db.execute_query_safe.assert_called_once()


class TestFetchQuerySafe:
    """Tests for fetch_query_safe function."""

    def test_delegates_to_db_fetch_query_safe(self, monkeypatch):
        """Test that function delegates to db.fetch_query_safe."""
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.fetch_query_safe.return_value = []
        monkeypatch.setattr("src.app_main.shared.domain.services.db_service._db", mock_db)

        result = fetch_query_safe("SELECT * FROM users")

        assert result == []
        mock_db.fetch_query_safe.assert_called_once()
