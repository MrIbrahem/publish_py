from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain_models import ViewsNewRecord
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


class TestListViewsNew:
    """Tests for list_views_new function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_views_new("t1", "en", 2023)
        add_views_new("t2", "en", 2023)
        result = list_views_new()
        assert len(result) >= 2


class TestListViewsByTarget:
    """Tests for list_views_by_target function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by target."""
        add_views_new("t1", "en", 2022)
        add_views_new("t1", "en", 2023)
        add_views_new("t2", "en", 2023)
        result = list_views_by_target("t1")
        assert len(result) == 2
        assert all(r.target == "t1" for r in result)


class TestListViewsByLang:
    """Tests for list_views_by_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns records by language."""
        add_views_new("t1", "en", 2023)
        add_views_new("t1", "fr", 2023)
        result = list_views_by_lang("fr")
        assert len(result) == 1
        assert result[0].lang == "fr"


class TestGetViewsNew:
    """Tests for get_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        v = add_views_new("t1", "en", 2023)
        result = get_views_new(v.id)
        assert isinstance(result, ViewsNewRecord)
        assert result.target == "t1"


class TestGetViewsByTargetLangYear:
    """Tests for get_views_by_target_lang_year function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by target, lang, and year."""
        add_views_new("t1", "en", 2023)
        result = get_views_by_target_lang_year("t1", "en", 2023)
        assert result.target == "t1"
        assert result.year == 2023


class TestAddViewsNew:
    """Tests for add_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_views_new("t1", "en", 2023, 100)
        assert record.target == "t1"
        assert record.views == 100


class TestAddOrUpdateViewsNew:
    """Tests for add_or_update_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_views_new("t1", "en", 2023, 10)
        record = add_or_update_views_new("t1", "en", 2023, 20)
        assert record.views == 20
        assert len(list_views_new()) == 1


class TestUpdateViewsNew:
    """Tests for update_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        v = add_views_new("t1", "en", 2023, 10)
        updated = update_views_new(v.id, views=20)
        assert updated.views == 20


class TestDeleteViewsNew:
    """Tests for delete_views_new function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        v = add_views_new("t1", "en", 2023)
        delete_views_new(v.id)
        assert get_views_new(v.id) is None


class TestGetTotalViewsForTarget:
    """Tests for get_total_views_for_target function."""

    def test_returns_sum_of_views(self, monkeypatch):
        """Test that function returns sum of views."""
        add_views_new("t1", "en", 2022, 100)
        add_views_new("t1", "fr", 2023, 200)
        assert get_total_views_for_target("t1") == 300

    def test_returns_zero_when_no_records(self, monkeypatch):
        """Test that function returns 0 when no records."""
        assert get_total_views_for_target("ghost") == 0

    def test_handles_none_views(self, monkeypatch):
        """Test that function handles None views."""
        add_views_new("t1", "en", 2022, None)
        assert get_total_views_for_target("t1") == 0
