"""
Integration tests for database operations.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.app_main.config import DbConfig
from src.app_main.shared.domain.db_ensure_service import ensure_db_tables


class TestDBIntegration:
    """Integration tests for DB with Database class."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database for testing."""
        with patch("src.app_main.shared.domain.db_ensure_service.Database") as MockDatabase:
            mock_db_instance = MagicMock()
            MockDatabase.return_value = mock_db_instance
            # Mock the table creation
            mock_db_instance.execute_query_safe.return_value = None
            yield mock_db_instance

    def test_db_creates_tables_on_init(self, mock_db):
        """Test that DB creates tables."""
        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        ensure_db_tables(config)

        # Should execute table creation queries for pages and pages_users tables
        calls = mock_db.execute_query_safe.mock_calls
        create_statements = [str(call) for call in calls]
        assert any("CREATE TABLE IF NOT EXISTS pages" in s for s in create_statements)
        assert any("CREATE TABLE IF NOT EXISTS pages_users" in s for s in create_statements)
        assert any("CREATE TABLE IF NOT EXISTS user_tokens" in s for s in create_statements)
        assert any("CREATE TABLE IF NOT EXISTS qids" in s for s in create_statements)
        assert any("CREATE TABLE IF NOT EXISTS publish_reports" in s for s in create_statements)
