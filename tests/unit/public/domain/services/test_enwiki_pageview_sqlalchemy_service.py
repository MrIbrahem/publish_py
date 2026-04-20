from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain.models import _EnwikiPageviewRecord
from src.sqlalchemy_app.public.domain.services.enwiki_pageview_service import (
    add_enwiki_pageview,
    add_or_update_enwiki_pageview,
    delete_enwiki_pageview,
    get_enwiki_pageview,
    get_enwiki_pageview_by_title,
    get_top_enwiki_pageviews,
    list_enwiki_pageviews,
    update_enwiki_pageview,
)
from src.sqlalchemy_app.public.domain_models import EnwikiPageviewRecord


def test_enwiki_pageview_workflow():
    # Test add
    p = add_enwiki_pageview("Anatomy", 5000)
    assert p.title == "Anatomy"
    assert p.en_views == 5000

    # Test get
    p2 = get_enwiki_pageview(p.id)
    assert p2.title == "Anatomy"

    # Test get by title
    p3 = get_enwiki_pageview_by_title("Anatomy")
    assert p3.id == p.id

    # Test list
    all_p = list_enwiki_pageviews()
    assert any(x.title == "Anatomy" for x in all_p)

    # Test top views
    top = get_top_enwiki_pageviews(1)
    assert top[0].title == "Anatomy"

    # Test update
    updated = update_enwiki_pageview(p.id, en_views=7500)
    assert updated.en_views == 7500

    # Test add_or_update
    p4 = add_or_update_enwiki_pageview("Anatomy", 10000)
    assert p4.en_views == 10000

    # Test delete
    delete_enwiki_pageview(p.id)
    assert get_enwiki_pageview(p.id) is None


class TestListEnwikiPageviews:
    """Tests for list_enwiki_pageviews function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_enwiki_pageview("Biology")
        add_enwiki_pageview("Chemistry")
        result = list_enwiki_pageviews()
        assert len(result) >= 2


class TestGetTopEnwikiPageviews:
    """Tests for get_top_enwiki_pageviews function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns top records by views."""
        add_enwiki_pageview("Physics", 100)
        add_enwiki_pageview("Mathematics", 1000)
        top = get_top_enwiki_pageviews(1)
        assert len(top) == 1
        assert top[0].title == "Mathematics"

    def test_uses_default_limit(self, monkeypatch):
        """Test that function uses default limit."""
        get_top_enwiki_pageviews()


class TestGetEnwikiPageview:
    """Tests for get_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        p = add_enwiki_pageview("Genetics")
        result = get_enwiki_pageview(p.id)
        assert isinstance(result, EnwikiPageviewRecord)
        assert result.title == "Genetics"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_enwiki_pageview(9999) is None


class TestGetEnwikiPageviewByTitle:
    """Tests for get_enwiki_pageview_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_enwiki_pageview("Microbiology")
        result = get_enwiki_pageview_by_title("Microbiology")
        assert result.title == "Microbiology"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_enwiki_pageview_by_title("Ghost") is None


class TestAddEnwikiPageview:
    """Tests for add_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_enwiki_pageview("Virology", 300)
        assert record.title == "Virology"
        assert record.en_views == 300

    def test_raises_error_if_exists(self, monkeypatch):
        add_enwiki_pageview("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_enwiki_pageview("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_enwiki_pageview("")


class TestAddOrUpdateEnwikiPageview:
    """Tests for add_or_update_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_enwiki_pageview("Epidemiology", 50)
        record = add_or_update_enwiki_pageview("Epidemiology", 150)
        assert record.en_views == 150
        assert len(list_enwiki_pageviews()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_or_update_enwiki_pageview("  ")


class TestUpdateEnwikiPageview:
    """Tests for update_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        p = add_enwiki_pageview("Immunology", 100)
        updated = update_enwiki_pageview(p.id, en_views=200)
        assert updated.en_views == 200

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        p = add_enwiki_pageview("No_Change")
        result = update_enwiki_pageview(p.id)
        assert result.title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_enwiki_pageview(9999, en_views=10)


class TestDeleteEnwikiPageview:
    """Tests for delete_enwiki_pageview function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        p = add_enwiki_pageview("Pathology")
        delete_enwiki_pageview(p.id)
        assert get_enwiki_pageview(p.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_enwiki_pageview(9999)
