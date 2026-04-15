"""Integration tests for database operations.

These tests verify the integration of Database class with the various DB modules.
"""

from unittest.mock import MagicMock, patch


class TestDatabaseIntegration:
    """Integration tests for Database class with DB modules."""

    def test_database_initialization(self):
        """Test that Database initializes with correct parameters."""
        from src.app_main.config import DbConfig
        from src.new_app.shared.db.db_class import Database

        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        with patch("src.new_app.shared.db.db_class.pymysql.connect") as mock_connect:
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
        from src.new_app.shared.db.db_class import Database

        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        with patch("src.new_app.shared.db.db_class.pymysql.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            db = Database(config)
            db.connection = mock_conn  # Set the connection directly

            with db:
                assert db is not None

            # Connection should be closed after exiting context
            mock_conn.close.assert_called_once()


class TestPagesDBIntegration:
    """Integration tests for PagesDB with Database class."""

    def test_pages_db_creates_tables_on_init(self):
        """Test that PagesDB creates tables on initialization."""
        from src.app_main.config import DbConfig
        from src.new_app.shared.db.db_Pages import PagesDB

        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        with patch("src.new_app.shared.db.db_Pages.Database") as MockDB:
            mock_db_instance = MagicMock()
            MockDB.return_value = mock_db_instance

            PagesDB(config)

            # Should execute table creation queries for pages and pages_users tables
            calls = mock_db_instance.execute_query_safe.mock_calls
            create_statements = [str(call) for call in calls]
            assert any("CREATE TABLE IF NOT EXISTS pages" in s for s in create_statements)
            assert any("CREATE TABLE IF NOT EXISTS pages_users" in s for s in create_statements)


class TestUserTokenDBIntegration:
    """Integration tests for UserTokenDB with Database class."""

    def test_user_token_db_creates_table_on_init(self):
        """Test that UserTokenDB creates table on initialization."""
        from src.app_main.config import DbConfig
        from src.new_app.shared.db.db_user_tokens import UserTokenDB

        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        with patch("src.new_app.shared.db.db_user_tokens.Database") as MockDB:
            mock_db_instance = MagicMock()
            MockDB.return_value = mock_db_instance

            UserTokenDB(config)

            # Should execute table creation query for user_tokens table
            calls = mock_db_instance.execute_query_safe.mock_calls
            create_statements = [str(call) for call in calls]
            assert any("CREATE TABLE IF NOT EXISTS user_tokens" in s for s in create_statements)


class TestQidsDBIntegration:
    """Integration tests for QidsDB with Database class."""

    def test_qids_db_creates_table_on_init(self):
        """Test that QidsDB creates table on initialization."""
        from src.app_main.config import DbConfig
        from src.new_app.shared.db.db_qids import QidsDB

        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        with patch("src.new_app.shared.db.db_qids.Database") as MockDB:
            mock_db_instance = MagicMock()
            MockDB.return_value = mock_db_instance

            QidsDB(config)

            # Should execute table creation query for qids table
            calls = mock_db_instance.execute_query_safe.mock_calls
            create_statements = [str(call) for call in calls]
            assert any("CREATE TABLE IF NOT EXISTS qids" in s for s in create_statements)


class TestReportsDBIntegration:
    """Integration tests for ReportsDB with Database class."""

    def test_reports_db_creates_table_on_init(self):
        """Test that ReportsDB creates table on initialization."""
        from src.app_main.config import DbConfig
        from src.new_app.shared.db.db_publish_reports import ReportsDB

        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        with patch("src.new_app.shared.db.db_publish_reports.Database") as MockDB:
            mock_db_instance = MagicMock()
            MockDB.return_value = mock_db_instance

            ReportsDB(config)

            # Should execute table creation query for publish_reports table
            calls = mock_db_instance.execute_query_safe.mock_calls
            create_statements = [str(call) for call in calls]
            assert any("CREATE TABLE IF NOT EXISTS publish_reports" in s for s in create_statements)


class TestCategoriesDBIntegration:
    """Integration tests for CategoriesDB with Database class."""

    def test_categories_db_creates_table_on_init(self):
        """Test that CategoriesDB creates table on initialization."""
        from src.app_main.config import DbConfig
        from src.new_app.shared.db.db_categories import CategoriesDB

        config = DbConfig(
            db_name="test_db",
            db_host="localhost",
            db_user="test_user",
            db_password="test_pass",
        )

        with patch("src.new_app.shared.db.db_categories.Database") as MockDB:
            mock_db_instance = MagicMock()
            MockDB.return_value = mock_db_instance

            CategoriesDB(config)

            # Should execute table creation query for categories table
            calls = mock_db_instance.execute_query_safe.mock_calls
            create_statements = [str(call) for call in calls]
            assert any("CREATE TABLE IF NOT EXISTS categories" in s for s in create_statements)
