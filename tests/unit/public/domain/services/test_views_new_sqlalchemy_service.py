from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain.models import _ViewsNewRecord
from src.sqlalchemy_app.public.domain.services.views_new_service import (
    add_or_update_views_new,
    add_views_new,
    delete_views_new,
    get_total_views_for_target,
    get_views_by_target_lang_year,
    get_views_new,
    list_views_by_lang,
    list_views_by_target,
    list_views_new,
    update_views_new,
)
from src.sqlalchemy_app.public.domain_models import ViewsNewRecord


def test_views_new_workflow():
    # Test add
    v = add_views_new("Dengue_fever", "en", 2023, 1500000)
    assert v.target == "Dengue_fever"
    assert v.views == 1500000

    # Test get
    v2 = get_views_new(v.id)
    assert v2.target == "Dengue_fever"

    # Test get by target, lang, year
    v3 = get_views_by_target_lang_year("Dengue_fever", "en", 2023)
    assert v3.id == v.id

    # Test list
    all_v = list_views_new()
    assert any(x.target == "Dengue_fever" for x in all_v)

    # Test list by target/lang
    by_target = list_views_by_target("Dengue_fever")
    assert len(by_target) >= 1
    by_lang = list_views_by_lang("en")
    assert len(by_lang) >= 1

    # Test update
    updated = update_views_new(v.id, views=1600000)
    assert updated.views == 1600000

    # Test total views
    total = get_total_views_for_target("Dengue_fever")
    assert total == 1600000

    # Test add_or_update
    v4 = add_or_update_views_new("Dengue_fever", "en", 2023, 1700000)
    assert v4.views == 1700000

    # Test delete
    delete_views_new(v.id)
    assert get_views_new(v.id) is None


class TestListViewsNew:
    """Tests for list_views_new function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_views_new("Malaria", "en", 2023)
        add_views_new("Cholera", "en", 2023)
        result = list_views_new()
        assert len(result) >= 2


class TestListViewsByTarget:
    """Tests for list_views_by_target function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by target."""
        add_views_new("Tuberculosis", "en", 2022)
        add_views_new("Tuberculosis", "en", 2023)
        add_views_new("Diabetes", "en", 2023)
        result = list_views_by_target("Tuberculosis")
        assert len(result) == 2
        assert all(r.target == "Tuberculosis" for r in result)


class TestListViewsByLang:
    """Tests for list_views_by_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by language."""
        add_views_new("Influenza", "en", 2023)
        add_views_new("Influenza", "fr", 2023)
        result = list_views_by_lang("fr")
        assert len(result) == 1
        assert result[0].lang == "fr"


class TestGetViewsNew:
    """Tests for get_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        v = add_views_new("Hepatitis_B", "en", 2023)
        result = get_views_new(v.id)
        assert isinstance(result, ViewsNewRecord)
        assert result.target == "Hepatitis_B"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_views_new(9999) is None


class TestGetViewsByTargetLangYear:
    """Tests for get_views_by_target_lang_year function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by target, lang, and year."""
        add_views_new("Measles", "en", 2023)
        result = get_views_by_target_lang_year("Measles", "en", 2023)
        assert result.target == "Measles"
        assert result.year == 2023

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_views_by_target_lang_year("Ghost", "en", 2023) is None


class TestAddViewsNew:
    """Tests for add_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_views_new("Smallpox", "en", 2023, 500000)
        assert record.target == "Smallpox"
        assert record.views == 500000

    def test_raises_error_if_exists(self, monkeypatch):
        add_views_new("Duplicate", "en", 2023)
        with pytest.raises(ValueError, match="already exists"):
            add_views_new("Duplicate", "en", 2023)

    def test_raises_error_if_no_target_or_lang(self, monkeypatch):
        with pytest.raises(ValueError, match="Target is required"):
            add_views_new("", "en", 2023)
        with pytest.raises(ValueError, match="Language is required"):
            add_views_new("T", " ", 2023)


class TestAddOrUpdateViewsNew:
    """Tests for add_or_update_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_views_new("Polio", "en", 2023, 100000)
        record = add_or_update_views_new("Polio", "en", 2023, 200000)
        assert record.views == 200000
        assert len(list_views_new()) == 1

    def test_raises_error_if_no_target_or_lang(self, monkeypatch):
        with pytest.raises(ValueError, match="Target is required"):
            add_or_update_views_new("", "en", 2023)
        with pytest.raises(ValueError, match="Language is required"):
            add_or_update_views_new("T", " ", 2023)


class TestUpdateViewsNew:
    """Tests for update_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        v = add_views_new("Stroke", "en", 2023, 1000000)
        updated = update_views_new(v.id, views=1100000)
        assert updated.views == 1100000

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        v = add_views_new("No_Change", "en", 2023)
        result = update_views_new(v.id)
        assert result.target == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_views_new(9999, views=10)


class TestDeleteViewsNew:
    """Tests for delete_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        v = add_views_new("Asthma", "en", 2023)
        delete_views_new(v.id)
        assert get_views_new(v.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_views_new(9999)


class TestGetTotalViewsForTarget:
    """Tests for get_total_views_for_target function."""

    def test_returns_sum_of_views(self, monkeypatch):
        """Test that function returns sum of views."""
        add_views_new("Cancer", "en", 2022, 5000000)
        add_views_new("Cancer", "fr", 2023, 1000000)
        assert get_total_views_for_target("Cancer") == 6000000

    def test_returns_zero_when_no_records(self, monkeypatch):
        """Test that function returns 0 when no records."""
        assert get_total_views_for_target("Ghost_Article") == 0

    def test_handles_none_views(self, monkeypatch):
        """Test that function handles None views."""
        add_views_new("Empty_Views", "en", 2022, None)
        assert get_total_views_for_target("Empty_Views") == 0
