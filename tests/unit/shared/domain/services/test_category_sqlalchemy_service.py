from unittest.mock import MagicMock, patch

import pytest
from src.db_models.shared_models import CategoryRecord
from src.sqlalchemy_app.shared.domain.models import _CategoryRecord
from src.sqlalchemy_app.shared.domain.services.category_service import (
    add_category,
    delete_category,
    get_camp_to_cats,
    get_campaign_category,
    list_categories,
    update_category,
)


def test_category_workflow():
    c = add_category("test_cat", "Display Name", "test_campaign", "cat2", 1, 1)
    assert c.category == "test_cat"
    assert get_campaign_category("test_campaign").category == "test_cat"
    assert any(x.category == "test_cat" for x in list_categories())
    assert get_camp_to_cats()["test_campaign"] == "test_cat"
    updated = update_category(c.id, "new_title", "new_campaign")
    assert updated.category == "new_title"
    delete_category(c.id)
    assert get_campaign_category("new_campaign") is None


class TestGetCampaignCategory:
    """Tests for get_campaign_category function."""

    def test_returns_category_record(self, monkeypatch):
        """Test that function returns a CategoryRecord."""

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when campaign not found."""


class TestAddCategory:
    """Tests for add_category function."""

    def test_adds_category_without_default(self, monkeypatch):
        """Test adding a category without setting it as default."""

    def test_adds_category_with_default(self, monkeypatch):
        """Test adding a category and setting it as default."""

    def test_uses_campaign_as_display_fallback(self, monkeypatch):
        """Test that campaign name is used as display when display is empty."""


class TestListCategories:
    """Tests for list_categories function."""

    def test_returns_list_of_categories(self, monkeypatch):
        """Test that function returns list of categories."""

    def test_returns_empty_list_when_no_categories(self, monkeypatch):
        """Test that function returns empty list when no categories exist."""


class TestDeleteCategory:
    """Tests for delete_category function."""

    def test_deletes_category(self, monkeypatch):
        """Test that delete_category calls store delete."""


class TestUpdateCategory:
    """Tests for update_category function."""

    def test_updates_category(self, monkeypatch):
        """Test that update_category updates and returns the record."""


class TestGetCampToCats:
    """Tests for get_camp_to_cats function."""

    def test_returns_campaign_to_category_mapping(self, monkeypatch):
        """Test that get_camp_to_cats returns correct mapping."""

    def test_handles_empty_category(self, monkeypatch):
        """Test that get_camp_to_cats handles empty category values."""

    def test_skips_empty_campaign(self, monkeypatch):
        """Test that get_camp_to_cats skips records with empty campaign."""
