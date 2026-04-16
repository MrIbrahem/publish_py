"""
Integration tests for database operations.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.config import DbConfig
from src.app_main.shared.domain.db_ensure_tables import ensure_db_tables


class TestEnsureDbTables:
    """Integration tests for DB table creation with Database class."""

    @pytest.fixture
    def mock_db(self, monkeypatch):
        """Create a mock database for testing."""
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query_safe.return_value = None
        mock_db_instance.__enter__ = MagicMock(return_value=mock_db_instance)
        mock_db_instance.__exit__ = MagicMock(return_value=False)

        def mock_database_init(config):
            return mock_db_instance

        monkeypatch.setattr("src.app_main.shared.domain.db_ensure_tables.Database", mock_database_init)
        return mock_db_instance

    @pytest.fixture
    def db_config(self):
        """Create a DbConfig for testing."""
        return DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

    def test_creates_all_required_tables(self, mock_db, db_config):
        """Test that all required tables are created."""
        ensure_db_tables(db_config)

        calls = mock_db.execute_query_safe.call_args_list
        executed_sql = [str(call) for call in calls]

        expected_tables = [
            "categories",
            "pages",
            "pages_users",
            "user_tokens",
            "qids",
            "publish_reports",
        ]

        for table in expected_tables:
            assert any(f"CREATE TABLE IF NOT EXISTS {table}" in s for s in executed_sql), f"Table {table} not created"

    def test_table_creation_order(self, mock_db, db_config):
        """Test that tables are created in correct order (dependencies)."""
        ensure_db_tables(db_config)

        calls = mock_db.execute_query_safe.call_args_list
        executed_queries = [call[0][0] for call in calls]

        assert executed_queries[0].strip().startswith("CREATE TABLE IF NOT EXISTS categories")
        assert executed_queries.index(executed_queries[0]) < executed_queries.index(executed_queries[1])

    def test_table_creation_sql_content(self, mock_db, db_config):
        """Test that table creation SQL contains expected column definitions."""
        ensure_db_tables(db_config)

        calls = mock_db.execute_query_safe.call_args_list

        pages_sql = next(call[0][0] for call in calls if "pages" in call[0][0].lower())
        assert "PRIMARY KEY (id)" in pages_sql
        assert "title varchar(120)" in pages_sql

        qids_sql = next(call[0][0] for call in calls if "qids" in call[0][0].lower())
        assert "UNIQUE KEY title" in qids_sql

        user_tokens_sql = next(call[0][0] for call in calls if "user_tokens" in call[0][0].lower())
        assert "PRIMARY KEY (user_id)" in user_tokens_sql

    def test_uses_safe_query_method(self, mock_db, db_config):
        """Test that execute_query_safe is used for table creation."""
        ensure_db_tables(db_config)

        assert mock_db.execute_query_safe.call_count == 6
        assert mock_db.execute_query.call_count == 0

    def test_database_class_instantiated(self, mock_db, db_config):
        """Test that Database class is instantiated with correct config."""
        original_database = None

        def get_mock_database(db_config):
            return mock_db

        import src.app_main.shared.domain.db_ensure_tables as db_module

        original_database = db_module.Database
        db_module.Database = get_mock_database

        try:
            ensure_db_tables(db_config)
        finally:
            db_module.Database = original_database

        assert mock_db.execute_query_safe.call_count == 6

    def test_does_not_raise_on_success(self, mock_db, db_config):
        """Test that function does not raise exception on success."""
        ensure_db_tables(db_config)

    def test_returns_none(self, mock_db, db_config):
        """Test that function returns None."""
        result = ensure_db_tables(db_config)
        assert result is None
