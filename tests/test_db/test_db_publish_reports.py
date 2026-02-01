"""Tests for db.db_publish_reports module."""

import pytest
from unittest.mock import patch, MagicMock


class TestQueryWithFilters:
    """Tests for ReportsDB.query_with_filters method."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database for testing."""
        with patch("src.app_main.db.db_publish_reports.Database") as MockDatabase:
            mock_db_instance = MagicMock()
            MockDatabase.return_value = mock_db_instance
            # Mock the table creation
            mock_db_instance.execute_query_safe.return_value = None
            yield mock_db_instance

    def test_filters_by_year(self, mock_db):
        """Test filtering by year."""
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "date": "2026-01-15",
                "title": "Test Page",
                "user": "TestUser",
                "lang": "en",
                "sourcetitle": "Source",
                "result": "success",
                "data": "{}",
            }
        ]

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        records = db.query_with_filters({"year": "2026"})

        assert len(records) == 1
        assert records[0].id == 1
        # Verify the query includes year filter
        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "YEAR(date) = %s" in query

    def test_filters_by_month(self, mock_db):
        """Test filtering by month."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({"month": "1"})

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "MONTH(date) = %s" in query

    def test_filters_by_user(self, mock_db):
        """Test filtering by user."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({"user": "TestUser"})

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "user = %s" in query

    def test_filters_by_lang(self, mock_db):
        """Test filtering by language."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({"lang": "ar"})

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "lang = %s" in query

    def test_filters_combined(self, mock_db):
        """Test combined parameter filters."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({"year": "2026", "user": "TestUser", "lang": "en"})

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "YEAR(date) = %s" in query
        assert "user = %s" in query
        assert "lang = %s" in query

    def test_special_value_not_empty(self, mock_db):
        """Test special value 'not_empty'."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({"result": "not_empty"})

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "(result != '' AND result IS NOT NULL)" in query

    def test_special_value_empty(self, mock_db):
        """Test special value 'empty'."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({"result": "empty"})

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "(result = '' OR result IS NULL)" in query

    def test_special_value_greater_than_zero(self, mock_db):
        """Test special value '>0'."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({"year": ">0"})

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "YEAR(date) > 0" in query

    def test_special_value_all_skipped(self, mock_db):
        """Test special value 'all' is skipped."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({"user": "all"})

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        # When all is skipped, user shouldn't appear in WHERE
        assert "user = " not in query or "WHERE" not in query

    def test_select_field_filtering(self, mock_db):
        """Test select field filtering."""
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "title": "Test",
                "date": "2026-01-15",
            }
        ]

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({}, select_fields=["title", "date"])

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        # id is always included
        assert "id" in query
        assert "title" in query
        assert "date" in query

    def test_limit_parameter(self, mock_db):
        """Test limit parameter."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({}, limit=10)

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "LIMIT %s" in query

    def test_invalid_select_fields_filtered(self, mock_db):
        """Test that invalid select fields are filtered out."""
        mock_db.fetch_query_safe.return_value = []

        from src.app_main.db.db_publish_reports import ReportsDB

        db = ReportsDB({"host": "test"})
        db.query_with_filters({}, select_fields=["title", "invalid_field", "date"])

        call_args = mock_db.fetch_query_safe.call_args
        query = call_args[0][0]
        assert "invalid_field" not in query
