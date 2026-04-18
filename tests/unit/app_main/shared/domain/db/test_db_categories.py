"""
Tests for db.db_categories module.
"""

from unittest.mock import MagicMock

import pytest
from src.app_main.config import DbConfig
from src.app_main.shared.domain.db.db_categories import (
    CategoriesDB,
)
from src.app_main.shared.domain.models import CategoryRecord


class TestCategoriesDB:
    """Tests for CategoriesDB class."""

    def test_fetch_by_id_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns CategoryRecord when ID exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "category": "TestCategory",
                "campaign": "TestCampaign",
                "display": "Test Display",
                "category2": "TestCategory2",
                "depth": 2,
                "is_default": 1,
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        result = categories_db.fetch_by_id(1)

        assert isinstance(result, CategoryRecord)
        assert result.id == 1
        assert result.category == "TestCategory"
        assert result.campaign == "TestCampaign"

    def test_fetch_by_id_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_id returns None when ID not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        result = categories_db.fetch_by_id(999)

        assert result is None

    def test_list_returns_all_records(self, monkeypatch, db_config):
        """Test that list returns all category records."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "category": "Category1",
                "campaign": "Campaign1",
                "display": "Display1",
                "category2": "",
                "depth": 0,
                "is_default": 0,
            },
            {
                "id": 2,
                "category": "Category2",
                "campaign": "Campaign2",
                "display": "Display2",
                "category2": "",
                "depth": 1,
                "is_default": 1,
            },
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        result = categories_db.list()

        assert len(result) == 2
        assert all(isinstance(r, CategoryRecord) for r in result)
        assert result[0].category == "Category1"
        assert result[1].category == "Category2"

    def test_list_returns_empty_list_when_no_records(self, monkeypatch, db_config):
        """Test that list returns empty list when no records exist."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        result = categories_db.list()

        assert result == []

    def test_fetch_by_campaign_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_campaign returns CategoryRecord when campaign exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "category": "TestCategory",
                "campaign": "TestCampaign",
                "display": "Test Display",
                "category2": "",
                "depth": 0,
                "is_default": 0,
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        result = categories_db.fetch_by_campaign("TestCampaign")

        assert isinstance(result, CategoryRecord)
        assert result.campaign == "TestCampaign"

    def test_fetch_by_campaign_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_campaign returns None when campaign not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        result = categories_db.fetch_by_campaign("NonExistentCampaign")

        assert result is None

    def test_fetch_by_category_returns_record_when_found(self, monkeypatch, db_config):
        """Test that fetch_by_category returns CategoryRecord when category exists."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "category": "TestCategory",
                "campaign": "TestCampaign",
                "display": "Test Display",
                "category2": "",
                "depth": 0,
                "is_default": 0,
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        result = categories_db.fetch_by_category("TestCategory")

        assert isinstance(result, CategoryRecord)
        assert result.category == "TestCategory"

    def test_fetch_by_category_returns_none_when_not_found(self, monkeypatch, db_config):
        """Test that fetch_by_category returns None when category not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        result = categories_db.fetch_by_category("NonExistentCategory")

        assert result is None

    def test_delete_removes_record(self, monkeypatch, db_config):
        """Test that delete removes a category record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "category": "TestCategory",
                "campaign": "TestCampaign",
                "display": "",
                "category2": "",
                "depth": 0,
                "is_default": 0,
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        categories_db.delete(1)

        mock_db.execute_query_safe.assert_called_with(
            "DELETE FROM categories WHERE id = %s",
            (1,),
        )

    def test_delete_raises_error_when_record_not_found(self, monkeypatch, db_config):
        """Test that delete raises ValueError when record not found."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = []

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        with pytest.raises(ValueError, match="Category with ID 999 not found"):
            categories_db.delete(999)

    def test_add_inserts_new_record(self, monkeypatch, db_config):
        """Test that add inserts a new category record."""
        mock_db = MagicMock()
        mock_db.fetch_query_safe.return_value = [
            {
                "id": 1,
                "category": "TestCategory",
                "campaign": "TestCampaign",
                "display": "Test Display",
                "category2": "",
                "depth": 0,
                "is_default": 0,
            }
        ]

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        result = categories_db.add("TestCategory", "TestCampaign", "Test Display")

        mock_db.execute_query_safe.assert_called_with(
            """
                INSERT INTO categories (category, campaign, display, category2, depth)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    campaign = VALUES(campaign),
                    display = VALUES(display),
                    category2 = VALUES(category2),
                    depth = VALUES(depth)
            """,
            ("TestCategory", "TestCampaign", "Test Display", "", 0),
        )
        assert isinstance(result, CategoryRecord)
        assert result.category == "TestCategory"

    def test_set_default_updates_record(self, monkeypatch, db_config):
        """Test that set_default updates the default flag."""
        mock_db = MagicMock()

        monkeypatch.setattr("src.app_main.shared.domain.db.db_categories.Database", lambda db_data: mock_db)

        categories_db = CategoriesDB(db_config)
        categories_db.set_default(1)

        mock_db.execute_query_safe.assert_called_with(
            "UPDATE categories SET is_default = CASE WHEN id = %s THEN 1 ELSE 0 END",
            (1,),
        )
