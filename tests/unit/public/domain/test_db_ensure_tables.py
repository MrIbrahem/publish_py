"""
Unit tests for domain/db_ensure_tables.py module.

Tests for ensure_db_tables function.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.config import DbConfig
from src.app_main.public.domain.db_ensure_tables import ensure_db_tables


class TestEnsureDbTables:
    """Tests for ensure_db_tables function."""

    def test_creates_all_tables(self, db_config):
        """Test that function creates all required tables."""
        mock_db_instance = MagicMock()
        mock_db_instance.__enter__ = MagicMock(return_value=mock_db_instance)
        mock_db_instance.__exit__ = MagicMock(return_value=False)

        with patch("src.app_main.public.domain.db_ensure_tables.Database") as MockDatabase:
            MockDatabase.return_value = mock_db_instance

            ensure_db_tables(db_config)

            assert mock_db_instance.execute_query_safe.call_count == 11

    def test_calls_assessments_table(self, db_config):
        """Test that assessments table is created."""
        mock_db_instance = MagicMock()
        mock_db_instance.__enter__ = MagicMock(return_value=mock_db_instance)
        mock_db_instance.__exit__ = MagicMock(return_value=False)

        with patch("src.app_main.public.domain.db_ensure_tables.Database") as MockDatabase:
            MockDatabase.return_value = mock_db_instance

            ensure_db_tables(db_config)

            calls = mock_db_instance.execute_query_safe.call_args_list
            call_queries = [str(c) for c in calls]
            assert any("assessments" in q for q in call_queries)

    def test_calls_enwiki_pageviews_table(self, db_config):
        """Test that enwiki_pageviews table is created."""
        mock_db_instance = MagicMock()
        mock_db_instance.__enter__ = MagicMock(return_value=mock_db_instance)
        mock_db_instance.__exit__ = MagicMock(return_value=False)

        with patch("src.app_main.public.domain.db_ensure_tables.Database") as MockDatabase:
            MockDatabase.return_value = mock_db_instance

            ensure_db_tables(db_config)

            calls = mock_db_instance.execute_query_safe.call_args_list
            call_queries = [str(c) for c in calls]
            assert any("enwiki_pageviews" in q for q in call_queries)

    def test_uses_context_manager(self, db_config):
        """Test that Database is used as context manager."""
        mock_db_instance = MagicMock()
        mock_db_instance.__enter__ = MagicMock(return_value=mock_db_instance)
        mock_db_instance.__exit__ = MagicMock(return_value=False)

        with patch("src.app_main.public.domain.db_ensure_tables.Database") as MockDatabase:
            MockDatabase.return_value = mock_db_instance

            ensure_db_tables(db_config)

            MockDatabase.assert_called_once()
            mock_db_instance.__enter__.assert_called_once()
            mock_db_instance.__exit__.assert_called_once()
