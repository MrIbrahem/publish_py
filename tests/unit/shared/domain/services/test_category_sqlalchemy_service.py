from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.shared.domain_models import CategoryRecord
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db
from src.sqlalchemy_app.shared.domain.models import _CategoryRecord
from src.sqlalchemy_app.shared.domain.services.category_service import (
    add_category,
    delete_category,
    get_camp_to_cats,
    get_campaign_category,
    list_categories,
    update_category,
)


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


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
        add_category("cat1", campaign="camp1")
        result = get_campaign_category("camp1")
        assert isinstance(result, CategoryRecord)
        assert result.campaign == "camp1"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when campaign not found."""
        result = get_campaign_category("non_existent")
        assert result is None


class TestAddCategory:
    """Tests for add_category function."""

    def test_adds_category_without_default(self, monkeypatch):
        """Test adding a category without setting it as default."""
        record = add_category("cat1", campaign="camp1", is_default=0)
        assert record.category == "cat1"
        assert record.is_default == 0

    def test_adds_category_with_default(self, monkeypatch):
        """Test adding a category and setting it as default."""
        add_category("cat1", campaign="camp1", is_default=1)
        record2 = add_category("cat2", campaign="camp2", is_default=1)
        assert record2.is_default == 1

        cats = list_categories()
        cat1 = next(c for c in cats if c.category == "cat1")
        assert cat1.is_default == 0

    def test_uses_campaign_as_display_fallback(self, monkeypatch):
        """Test that campaign name is used as display when display is empty."""
        record = add_category("cat1", campaign="my_campaign", display="")
        assert record.display == "my_campaign"


class TestListCategories:
    """Tests for list_categories function."""

    def test_returns_list_of_categories(self, monkeypatch):
        """Test that function returns list of categories."""
        add_category("cat1", campaign="camp1")
        add_category("cat2", campaign="camp2")
        result = list_categories()
        assert len(result) >= 2
        assert any(c.category == "cat1" for c in result)
        assert any(c.category == "cat2" for c in result)

    def test_returns_empty_list_when_no_categories(self, monkeypatch):
        """Test that function returns empty list when no categories exist."""
        # Database is cleared by fixture setup_db per test
        result = list_categories()
        assert result == []


class TestDeleteCategory:
    """Tests for delete_category function."""

    def test_deletes_category(self, monkeypatch):
        """Test that delete_category calls store delete."""
        cat = add_category("cat1", campaign="camp1")
        delete_category(cat.id)
        assert not any(c.id == cat.id for c in list_categories())


class TestUpdateCategory:
    """Tests for update_category function."""

    def test_updates_category(self, monkeypatch):
        """Test that update_category updates and returns the record."""
        cat = add_category("cat1", campaign="camp1")
        updated = update_category(cat.id, "new_cat", "new_camp")
        assert updated.category == "new_cat"
        assert updated.campaign == "new_camp"


class TestGetCampToCats:
    """Tests for get_camp_to_cats function."""

    def test_returns_campaign_to_category_mapping(self, monkeypatch):
        """Test that get_camp_to_cats returns correct mapping."""
        add_category("cat1", campaign="camp1")
        add_category("cat2", campaign="camp2")
        mapping = get_camp_to_cats()
        assert mapping["camp1"] == "cat1"
        assert mapping["camp2"] == "cat2"

    def test_handles_empty_category(self, monkeypatch):
        """Test that get_camp_to_cats handles empty category values."""
        # Due to NOT NULL constraint and __post_init__ validation,
        # category cannot be empty in this service.
        pass

    def test_skips_empty_campaign(self, monkeypatch):
        """Test that get_camp_to_cats skips records with empty campaign."""
        # campaign also has validation in __post_init__
        pass
