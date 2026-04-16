"""
Tests for db.db_categories module.

TODO: CategoriesDB has major updates, we should rewrite related tests.
"""

from unittest.mock import MagicMock

import pytest
from src.app_main.config import DbConfig
from src.app_main.shared.domain.db.db_categories import (
    CategoriesDB,
)


@pytest.fixture
def fixture_for_category_db() -> DbConfig:
    """Fixture for DbConfig instance."""
    return DbConfig(
        db_name="localhost",
        db_host="localhost",
        db_user="user",
        db_password="pass",
    )


class TestCategoriesDB:
    """Tests for CategoriesDB class."""

    def test_retrieve_campaign_categories_returns_mapping(self, monkeypatch, fixture_for_category_db):
        """Test that list returns category mapping."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "campaign1", "category": "Category:Health"},
            {"campaign": "campaign2", "category": "Category:Science"},
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.list()

        assert result["campaign1"] == "Category:Health"
        assert result["campaign2"] == "Category:Science"

    def test_retrieve_campaign_categories_handles_empty_result(self, monkeypatch, fixture_for_category_db):
        """Test that empty result is handled gracefully."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.list()

        assert result == {}

    def test_retrieve_campaign_categories_handles_null_category(self, monkeypatch, fixture_for_category_db):
        """Test that null category values are handled."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "campaign1", "category": None},
            {"campaign": "campaign2", "category": "Category:Valid"},
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.list()

        assert result["campaign1"] == ""
        assert result["campaign2"] == "Category:Valid"

    def test_fetch_by_campaign_returns_category(self, monkeypatch, fixture_for_category_db):
        """Test that fetch_by_campaign returns correct category."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "test_campaign", "category": "Test Category"},
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.fetch_by_campaign("test_campaign")

        assert result == "Test Category"

    def test_fetch_by_campaign_returns_empty_for_missing(self, monkeypatch, fixture_for_category_db):
        """Test that empty string is returned for missing campaign."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {"campaign": "other_campaign", "category": "Other Category"},
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)
        categories_db = CategoriesDB(fixture_for_category_db)
        result = categories_db.fetch_by_campaign("missing_campaign")

        assert result == ""
