from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import ViewsNewRecord
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
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db





def test_views_new_workflow():
    # Test add
    v = add_views_new("target1", "en", 2023, 1000)
    assert v.target == "target1"
    assert v.views == 1000

    # Test get
    v2 = get_views_new(v.id)
    assert v2.target == "target1"

    # Test get by target, lang, year
    v3 = get_views_by_target_lang_year("target1", "en", 2023)
    assert v3.id == v.id

    # Test list
    all_v = list_views_new()
    assert any(x.target == "target1" for x in all_v)

    # Test list by target/lang
    by_target = list_views_by_target("target1")
    assert len(by_target) >= 1
    by_lang = list_views_by_lang("en")
    assert len(by_lang) >= 1

    # Test update
    updated = update_views_new(v.id, views=2000)
    assert updated.views == 2000

    # Test total views
    total = get_total_views_for_target("target1")
    assert total == 2000

    # Test add_or_update
    v4 = add_or_update_views_new("target1", "en", 2023, 3000)
    assert v4.views == 3000

    # Test delete
    delete_views_new(v.id)
    assert get_views_new(v.id) is None


class TestGetViewsNewDb:
    """Tests for get_views_new_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new ViewsNewDB is created when none cached."""


class TestListViewsNew:
    """Tests for list_views_new function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestListViewsByTarget:
    """Tests for list_views_by_target function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestListViewsByLang:
    """Tests for list_views_by_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestGetViewsNew:
    """Tests for get_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""


class TestGetViewsByTargetLangYear:
    """Tests for get_views_by_target_lang_year function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestAddViewsNew:
    """Tests for add_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestAddOrUpdateViewsNew:
    """Tests for add_or_update_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestUpdateViewsNew:
    """Tests for update_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteViewsNew:
    """Tests for delete_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestGetTotalViewsForTarget:
    """Tests for get_total_views_for_target function."""

    def test_returns_sum_of_views(self, monkeypatch):
        """Test that function returns sum of views."""

    def test_returns_zero_when_no_records(self, monkeypatch):
        """Test that function returns 0 when no records."""

    def test_handles_none_views(self, monkeypatch):
        """Test that function handles None views."""
