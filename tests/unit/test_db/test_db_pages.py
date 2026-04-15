"""Unit tests for db.db_Pages module.

Tests for Pages database operations.
"""

from unittest.mock import MagicMock, patch

import pytest
import pymysql

from src.app_main.config import DbConfig
from src.app_main.db.db_Pages import (
    PageRecord,
    PagesDB,
)


@pytest.fixture
def db_config():
    """Fixture for DbConfig instance."""
    return DbConfig(
        db_name="test_db",
        db_host="localhost",
        db_user="user",
        db_password="pass",
    )


@pytest.fixture
def sample_page_row():
    """Fixture for a sample page row from database."""
    return {
        "id": 1,
        "title": "TestPage",
        "word": 100,
        "translate_type": "Lead",
        "cat": "Category:Health",
        "lang": "ar",
        "user": "TestUser",
        "target": "TargetPage",
        "date": "2024-01-01",
        "pupdate": "2024-01-01",
        "add_date": "2024-01-01",
        "deleted": 0,
        "mdwiki_revid": 12345,
    }


class TestPageRecord:
    """Tests for PageRecord dataclass."""

    def test_create_with_required_fields(self):
        """Test creating PageRecord with required fields."""
        record = PageRecord(id=1, title="TestPage")
        assert record.id == 1
        assert record.title == "TestPage"
        assert record.word is None
        assert record.deleted == 0  # Default value

    def test_create_with_all_fields(self, sample_page_row):
        """Test creating PageRecord with all fields."""
        record = PageRecord(**sample_page_row)
        assert record.id == 1
        assert record.title == "TestPage"
        assert record.word == 100
        assert record.translate_type == "Lead"
        assert record.mdwiki_revid == 12345


class TestPagesDB:
    """Tests for PagesDB class."""

    def test_init_creates_database(self, monkeypatch, db_config):
        """Test that initialization creates a Database instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)

        assert pages_db.db is mock_db
        # Should call execute_query_safe twice (for pages and pages_users tables)
        assert mock_db.execute_query_safe.call_count == 2

    def test_list_returns_all_pages(self, monkeypatch, db_config, sample_page_row):
        """Test that list returns all page records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_page_row, {**sample_page_row, "id": 2, "title": "Page2"}]

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        result = pages_db.list()

        assert len(result) == 2
        assert all(isinstance(r, PageRecord) for r in result)
        assert result[0].id == 1
        assert result[1].id == 2
        mock_db.fetch_query_safe.assert_called_with("SELECT * FROM pages ORDER BY id ASC")

    def test_add_requires_non_empty_title(self, monkeypatch, db_config):
        """Test that add requires non-empty title."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        with pytest.raises(ValueError, match="Title is required"):
            pages_db.add("")

        with pytest.raises(ValueError, match="Title is required"):
            pages_db.add("   ")

    def test_add_strips_whitespace_from_title(self, monkeypatch, db_config):
        """Test that add strips whitespace from title."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "title": "TestPage"}]

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        pages_db.add("  TestPage  ")

        # Check that stripped title was used in INSERT
        call_args = mock_db.execute_query.call_args
        assert "TestPage" in call_args[0][1]
        assert "  TestPage  " not in call_args[0][1]

    def test_add_raises_on_duplicate(self, monkeypatch, db_config):
        """Test that add raises ValueError on duplicate title."""
        mock_db = MagicMock()
        mock_db.execute_query.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        with pytest.raises(ValueError, match="Page 'TestPage' already exists"):
            pages_db.add("TestPage")

    def test_fetch_by_id_raises_lookup_error_when_not_found(self, monkeypatch, db_config):
        """Test that _fetch_by_id raises LookupError when page not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        with pytest.raises(LookupError, match="Page id 999 was not found"):
            pages_db._fetch_by_id(999)

    def test_fetch_by_title_raises_lookup_error_when_not_found(self, monkeypatch, db_config):
        """Test that _fetch_by_title raises LookupError when page not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        with pytest.raises(LookupError, match="Page 'MissingPage' was not found"):
            pages_db._fetch_by_title("MissingPage")

    def test_update_returns_record_unchanged_when_no_kwargs(self, monkeypatch, db_config, sample_page_row):
        """Test that update returns record unchanged when no fields to update."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_page_row]

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        # Reset mock to ignore calls made during initialization (_ensure_table)
        mock_db.execute_query_safe.reset_mock()
        result = pages_db.update(1)

        # Should not execute update query when no kwargs provided
        mock_db.execute_query_safe.assert_not_called()
        assert result.id == 1

    def test_update_executes_update_query(self, monkeypatch, db_config, sample_page_row):
        """Test that update executes correct UPDATE query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_page_row]

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        pages_db.update(1, title="NewTitle", word=200)

        call_args = mock_db.execute_query_safe.call_args
        assert "UPDATE pages SET" in call_args[0][0]
        assert "`title` = %s" in call_args[0][0]
        assert "`word` = %s" in call_args[0][0]
        assert call_args[0][1] == ("NewTitle", 200, 1)

    def test_delete_raises_lookup_error_when_not_found(self, monkeypatch, db_config):
        """Test that delete raises LookupError when page not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        with pytest.raises(LookupError, match="Page id 999 was not found"):
            pages_db.delete(999)

    def test_delete_removes_record(self, monkeypatch, db_config, sample_page_row):
        """Test that delete removes the record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [sample_page_row]

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        result = pages_db.delete(1)

        assert result.id == 1
        mock_db.execute_query_safe.assert_called_with(
            "DELETE FROM pages WHERE id = %s",
            (1,),
        )

    def test_add_or_update_executes_upsert(self, monkeypatch, db_config):
        """Test that add_or_update executes correct upsert query."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "title": "TestPage"}]

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        pages_db.add_or_update("TestPage", word=100)

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO pages" in call_args[0][0]
        assert "ON DUPLICATE KEY UPDATE" in call_args[0][0]

    def test_find_exists_or_update_returns_true_when_exists(self, monkeypatch, db_config):
        """Test that _find_exists_or_update returns True when record exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [{"id": 1, "title": "Test"}]

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        result = pages_db._find_exists_or_update("Test", "ar", "User", "Target", False)

        assert result is True
        # Should also execute update query
        assert mock_db.execute_query_safe.call_count >= 1

    def test_find_exists_or_update_returns_false_when_not_exists(self, monkeypatch, db_config):
        """Test that _find_exists_or_update returns False when record doesn't exist."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        result = pages_db._find_exists_or_update("Test", "ar", "User", "Target", False)

        assert result is False

    def test_insert_page_target_executes_insert(self, monkeypatch, db_config):
        """Test that insert_page_target executes correct INSERT query."""
        mock_db = MagicMock()

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        result = pages_db.insert_page_target(
            sourcetitle="Source",
            tr_type="Lead",
            cat="Category:Health",
            lang="ar",
            user="TestUser",
            target="Target",
            table_name="pages",
            mdwiki_revid=12345,
            word=100,
        )

        call_args = mock_db.execute_query_safe.call_args
        assert "INSERT INTO pages" in call_args[0][0]
        params = call_args[0][1]
        assert params[0] == "Source"  # sourcetitle
        assert params[1] == 100  # word
        assert params[2] == "Lead"  # tr_type
        assert params[3] == "Category:Health"  # cat
        assert params[4] == "ar"  # lang
        assert params[5] == "TestUser"  # user
        assert params[6] == "Target"  # target
        assert params[7] == 12345  # mdwiki_revid

    def test_insert_page_target_returns_true_on_success(self, monkeypatch, db_config):
        """Test that insert_page_target returns True on success."""
        mock_db = MagicMock()

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        result = pages_db.insert_page_target(
            sourcetitle="Source",
            tr_type="Lead",
            cat="Category",
            lang="ar",
            user="User",
            target="Target",
            table_name="pages",
        )

        assert result is True

    def test_insert_page_target_returns_error_on_failure(self, monkeypatch, db_config):
        """Test that insert_page_target returns error string on failure."""
        mock_db = MagicMock()

        monkeypatch.setattr("src.app_main.db.db_Pages.Database", lambda db_data: mock_db)

        pages_db = PagesDB(db_config)
        # Now set the side_effect to raise an exception for subsequent calls
        mock_db.execute_query_safe.side_effect = Exception("DB Error")

        result = pages_db.insert_page_target(
            sourcetitle="Source",
            tr_type="Lead",
            cat="Category",
            lang="ar",
            user="User",
            target="Target",
            table_name="pages",
        )

        assert "DB Error" in result
