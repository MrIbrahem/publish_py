"""Integration tests for database operations.

These tests verify the integration of Database class with the various DB modules.
"""

from unittest.mock import MagicMock, patch


class TestDatabaseIntegration:
    """Integration tests for Database class with DB modules."""

    def test_database_initialization(self):
        """Test that Database initializes with correct parameters."""
        from src.app_main.config import DbConfig
        from src.app_main.shared.core.db_driver import Database

        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        with patch("src.app_main.shared.core.db_driver.pymysql.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            db = Database(config)
            db._connect()

            mock_connect.assert_called_once()
            call_kwargs = mock_connect.call_args.kwargs
            assert call_kwargs["host"] == "localhost"
            assert call_kwargs["database"] == "test_db"
            assert call_kwargs["user"] == "test_user"
            assert call_kwargs["password"] == "test_pass"

    def test_database_context_manager(self):
        """Test that Database works as context manager."""
        from src.app_main.config import DbConfig
        from src.app_main.shared.core.db_driver import Database

        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        with patch("src.app_main.shared.core.db_driver.pymysql.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            db = Database(config)
            db.connection = mock_conn  # Set the connection directly

            with db:
                assert db is not None

            # Connection should be closed after exiting context
            mock_conn.close.assert_called_once()
