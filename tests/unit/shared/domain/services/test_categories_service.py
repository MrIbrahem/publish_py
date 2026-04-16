"""
Unit tests for categories_service module.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.domain.services.categories_service import (
    add_category,
    delete_category,
    get_campaign_category,
    list_categories,
    update_category,
    get_camp_to_cats,
)


class TestGetCampaignCategory:
    """Tests for get_campaign_category function."""

    def test_returns_category_record(self, monkeypatch):
        """Test that function returns a CategoryRecord."""
        mock_store = MagicMock()
        mock_category = MagicMock()
        mock_store.fetch_by_campaign.return_value = mock_category
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = get_campaign_category("TestCampaign")

        assert result is mock_category
        mock_store.fetch_by_campaign.assert_called_once_with("TestCampaign")

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when campaign not found."""
        mock_store = MagicMock()
        mock_store.fetch_by_campaign.return_value = None
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = get_campaign_category("NonExistentCampaign")

        assert result is None


class TestAddCategory:
    """Tests for add_category function."""

    def test_adds_category_without_default(self, monkeypatch):
        """Test adding a category without setting it as default."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = add_category(
            category="TestCategory",
            display="Test Display",
            campaign="TestCampaign",
            category2="TestCategory2",
            depth=2,
            is_default=0,
        )

        mock_store.add.assert_called_once_with("TestCategory", "Test Display", "TestCampaign", "TestCategory2", 2)
        mock_store.set_default.assert_not_called()
        assert result is mock_record

    def test_adds_category_with_default(self, monkeypatch):
        """Test adding a category and setting it as default."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_record.id = 1
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = add_category(
            category="TestCategory",
            display="Test Display",
            campaign="TestCampaign",
            is_default=1,
        )

        mock_store.add.assert_called_once()
        mock_store.set_default.assert_called_once_with(1)
        assert result is mock_record

    def test_uses_campaign_as_display_fallback(self, monkeypatch):
        """Test that campaign name is used as display when display is empty."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = add_category(
            category="TestCategory",
            campaign="TestCampaign",
        )

        mock_store.add.assert_called_once_with("TestCategory", "TestCampaign", "TestCampaign", "", 0)


class TestListCategories:
    """Tests for list_categories function."""

    def test_returns_list_of_categories(self, monkeypatch):
        """Test that function returns list of categories."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = list_categories()

        assert result == mock_records
        mock_store.list.assert_called_once()

    def test_returns_empty_list_when_no_categories(self, monkeypatch):
        """Test that function returns empty list when no categories exist."""
        mock_store = MagicMock()
        mock_store.list.return_value = []
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = list_categories()

        assert result == []


class TestDeleteCategory:
    """Tests for delete_category function."""

    def test_deletes_category(self, monkeypatch):
        """Test that delete_category calls store delete."""
        mock_store = MagicMock()
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        delete_category(1)

        mock_store.delete.assert_called_once_with(1)


class TestUpdateCategory:
    """Tests for update_category function."""

    def test_updates_category(self, monkeypatch):
        """Test that update_category updates and returns the record."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = update_category(1, "UpdatedTitle", "UpdatedFile")

        mock_store.update.assert_called_once_with(1, "UpdatedTitle", "UpdatedFile")
        assert result is mock_record


class TestGetCampToCats:
    """Tests for get_camp_to_cats function."""

    def test_returns_campaign_to_category_mapping(self, monkeypatch):
        """Test that get_camp_to_cats returns correct mapping."""
        mock_record1 = MagicMock()
        mock_record1.campaign = "Campaign1"
        mock_record1.category = "Category1"

        mock_record2 = MagicMock()
        mock_record2.campaign = "Campaign2"
        mock_record2.category = "Category2"

        mock_store = MagicMock()
        mock_store.list.return_value = [mock_record1, mock_record2]
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = get_camp_to_cats()

        assert result == {"Campaign1": "Category1", "Campaign2": "Category2"}

    def test_handles_empty_category(self, monkeypatch):
        """Test that get_camp_to_cats handles empty category values."""
        mock_record = MagicMock()
        mock_record.campaign = "Campaign1"
        mock_record.category = None

        mock_store = MagicMock()
        mock_store.list.return_value = [mock_record]
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = get_camp_to_cats()

        assert result == {"Campaign1": ""}

    def test_skips_empty_campaign(self, monkeypatch):
        """Test that get_camp_to_cats skips records with empty campaign."""
        mock_record = MagicMock()
        mock_record.campaign = ""
        mock_record.category = "Category1"

        mock_store = MagicMock()
        mock_store.list.return_value = [mock_record]
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = get_camp_to_cats()

        assert result == {}
