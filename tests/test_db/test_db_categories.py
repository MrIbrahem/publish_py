"""Tests for db.db_categories module."""

from unittest.mock import MagicMock

import pytest

from src.app_main.config import DbConfig
from src.app_main.db.db_categories import (
    CategoriesDB,
    clear_categories_cache,
    get_campaign_category,
)


@pytest.fixture
def fixture_for_category_db() -> DbConfig:
    """Fixture for DbConfig instance."""
    return DbConfig(
        db_name="localhost",
        db_host="localhost",
        db_user="user",
        db_password="pass",
        db_connect_file=None,
    )


class TestCategoriesDB:
    """Tests for CategoriesDB class."""

    def test_retrieve_campaign_categories_returns_mapping(self, monkeypatch, fixture_for_category_db):
        """Test that retrieve_campaign_categories returns category mapping."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "campaign1", "category": "Category:Health"},
            {"campaign": "campaign2", "category": "Category:Science"},
        ]

        monkeypatch.setattr("src.app_main.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.retrieve_campaign_categories()

        assert result["campaign1"] == "Category:Health"
        assert result["campaign2"] == "Category:Science"

    def test_retrieve_campaign_categories_handles_empty_result(self, monkeypatch, fixture_for_category_db):
        """Test that empty result is handled gracefully."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.retrieve_campaign_categories()

        assert result == {}

    def test_retrieve_campaign_categories_handles_null_category(self, monkeypatch, fixture_for_category_db):
        """Test that null category values are handled."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "campaign1", "category": None},
            {"campaign": "campaign2", "category": "Category:Valid"},
        ]

        monkeypatch.setattr("src.app_main.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.retrieve_campaign_categories()

        assert result["campaign1"] == ""
        assert result["campaign2"] == "Category:Valid"

    def test_get_category_for_campaign_returns_category(self, monkeypatch, fixture_for_category_db):
        """Test that get_category_for_campaign returns correct category."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "test_campaign", "category": "Test Category"},
        ]

        monkeypatch.setattr("src.app_main.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.get_category_for_campaign("test_campaign")

        assert result == "Test Category"

    def test_get_category_for_campaign_returns_empty_for_missing(self, monkeypatch, fixture_for_category_db):
        """Test that empty string is returned for missing campaign."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "other_campaign", "category": "Other Category"},
        ]

        monkeypatch.setattr("src.app_main.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.get_category_for_campaign("missing_campaign")

        assert result == ""


class TestGetCampaignCategory:
    """Tests for get_campaign_category function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_categories_cache()

    def test_returns_category_for_campaign(self, monkeypatch):
        """Test that get_campaign_category returns correct category."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "test", "category": "TestCategory"},
        ]

        monkeypatch.setattr("src.app_main.db.db_categories.Database", lambda db_data: mock_db)
        clear_categories_cache()
        result = get_campaign_category("test", {"host": "test"})
        assert result == "TestCategory"

    def test_returns_empty_for_missing_campaign(self, monkeypatch):
        """Test that empty string is returned for missing campaign."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.db.db_categories.Database", lambda db_data: mock_db)
        clear_categories_cache()
        result = get_campaign_category("missing", {"host": "test"})
        assert result == ""


class TestClearCategoriesCache:
    """Tests for clear_categories_cache function."""

    def test_clears_cache(self, monkeypatch):
        """Test that clear_categories_cache clears the cache."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "test", "category": "Category1"},
        ]

        monkeypatch.setattr("src.app_main.db.db_categories.Database", lambda db_data: mock_db)
        clear_categories_cache()
        result1 = get_campaign_category("test", {"host": "test"})

        # Change mock return value
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "test", "category": "Category2"},
        ]

        # Should still return cached value
        result2 = get_campaign_category("test", {"host": "test"})
        assert result2 == result1

        # Clear cache
        clear_categories_cache()

        # Should now return new value
        result3 = get_campaign_category("test", {"host": "test"})
        assert result3 == "Category2"
