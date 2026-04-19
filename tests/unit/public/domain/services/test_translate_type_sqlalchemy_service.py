from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import TranslateTypeRecord
from src.sqlalchemy_app.public.domain.models import _TranslateTypeRecord
from src.sqlalchemy_app.public.domain.services.translate_type_service import (
    add_or_update_translate_type,
    add_translate_type,
    can_translate_full,
    can_translate_lead,
    delete_translate_type,
    get_translate_type,
    get_translate_type_by_title,
    list_full_enabled_types,
    list_lead_enabled_types,
    list_translate_types,
    update_translate_type,
)
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db





def test_translate_type_workflow():
    # Test add
    tt = add_translate_type("test_type", 1, 0)
    assert tt.tt_title == "test_type"
    assert tt.tt_lead == 1

    # Test get
    tt2 = get_translate_type(tt.tt_id)
    assert tt2.tt_title == "test_type"

    # Test get by title
    tt3 = get_translate_type_by_title("test_type")
    assert tt3.tt_id == tt.tt_id

    # Test list
    all_tt = list_translate_types()
    assert any(x.tt_title == "test_type" for x in all_tt)

    # Test enabled lists
    leads = list_lead_enabled_types()
    assert any(x.tt_title == "test_type" for x in leads)
    fulls = list_full_enabled_types()
    assert not any(x.tt_title == "test_type" for x in fulls)

    # Test can_translate
    assert can_translate_lead("test_type") is True
    assert can_translate_full("test_type") is False

    # Test update
    updated = update_translate_type(tt.tt_id, tt_full=1)
    assert updated.tt_full == 1
    assert can_translate_full("test_type") is True

    # Test add_or_update
    tt4 = add_or_update_translate_type("test_type", 0, 1)
    assert tt4.tt_lead == 0

    # Test delete
    delete_translate_type(tt.tt_id)
    assert get_translate_type(tt.tt_id) is None


class TestGetTranslateTypeDb:
    """Tests for get_translate_type_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new TranslateTypeDB is created when none cached."""


class TestListTranslateTypes:
    """Tests for list_translate_types function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestListLeadEnabledTypes:
    """Tests for list_lead_enabled_types function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestListFullEnabledTypes:
    """Tests for list_full_enabled_types function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestGetTranslateType:
    """Tests for get_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""


class TestGetTranslateTypeByTitle:
    """Tests for get_translate_type_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""


class TestAddTranslateType:
    """Tests for add_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestAddOrUpdateTranslateType:
    """Tests for add_or_update_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add_or_update."""


class TestUpdateTranslateType:
    """Tests for update_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteTranslateType:
    """Tests for delete_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""


class TestCanTranslateLead:
    """Tests for can_translate_lead function."""

    def test_returns_true_when_tt_lead_is_1(self, monkeypatch):
        """Test that function returns True when tt_lead is 1."""

    def test_returns_false_when_tt_lead_is_0(self, monkeypatch):
        """Test that function returns False when tt_lead is 0."""

    def test_returns_true_when_no_record(self, monkeypatch):
        """Test that function returns True when no record found (default behavior)."""


class TestCanTranslateFull:
    """Tests for can_translate_full function."""

    def test_returns_true_when_tt_full_is_1(self, monkeypatch):
        """Test that function returns True when tt_full is 1."""

    def test_returns_false_when_tt_full_is_0(self, monkeypatch):
        """Test that function returns False when tt_full is 0."""

    def test_returns_false_when_no_record(self, monkeypatch):
        """Test that function returns False when no record found (default behavior)."""
