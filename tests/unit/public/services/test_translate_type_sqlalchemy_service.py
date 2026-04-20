from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.models import _TranslateTypeRecord
from src.sqlalchemy_app.public.services.translate_type_service import (
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
from src.sqlalchemy_app.shared.db_models.public_models import TranslateTypeRecord


def test_translate_type_workflow():
    # Test add
    tt = add_translate_type("Medical history", 1, 0)
    assert tt.tt_title == "Medical history"
    assert tt.tt_lead == 1

    # Test get
    tt2 = get_translate_type(tt.tt_id)
    assert tt2.tt_title == "Medical history"

    # Test get by title
    tt3 = get_translate_type_by_title("Medical history")
    assert tt3.tt_id == tt.tt_id

    # Test list
    all_tt = list_translate_types()
    assert any(x.tt_title == "Medical history" for x in all_tt)

    # Test enabled lists
    leads = list_lead_enabled_types()
    assert any(x.tt_title == "Medical history" for x in leads)
    fulls = list_full_enabled_types()
    assert not any(x.tt_title == "Medical history" for x in fulls)

    # Test can_translate
    assert can_translate_lead("Medical history") is True
    assert can_translate_full("Medical history") is False

    # Test update
    updated = update_translate_type(tt.tt_id, tt_full=1)
    assert updated.tt_full == 1
    assert can_translate_full("Medical history") is True

    # Test add_or_update
    tt4 = add_or_update_translate_type("Medical history", 0, 1)
    assert tt4.tt_lead == 0

    # Test delete
    delete_translate_type(tt.tt_id)
    assert get_translate_type(tt.tt_id) is None


class TestListTranslateTypes:
    """Tests for list_translate_types function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_translate_type("Clinical trial")
        add_translate_type("Case study")
        result = list_translate_types()
        assert len(result) >= 2


class TestListLeadEnabledTypes:
    """Tests for list_lead_enabled_types function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list of lead enabled types."""
        add_translate_type("Epidemiology study", tt_lead=1)
        add_translate_type("In vitro study", tt_lead=0)
        result = list_lead_enabled_types()
        assert len(result) == 1
        assert result[0].tt_title == "Epidemiology study"


class TestListFullEnabledTypes:
    """Tests for list_full_enabled_types function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list of full enabled types."""
        add_translate_type("Systematic review", tt_full=1)
        add_translate_type("Meta-analysis", tt_full=0)
        result = list_full_enabled_types()
        assert len(result) == 1
        assert result[0].tt_title == "Systematic review"


class TestGetTranslateType:
    """Tests for get_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        tt = add_translate_type("Cohort study")
        result = get_translate_type(tt.tt_id)
        assert isinstance(result, TranslateTypeRecord)
        assert result.tt_title == "Cohort study"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_translate_type(9999) is None


class TestGetTranslateTypeByTitle:
    """Tests for get_translate_type_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_translate_type("Diagnostic test")
        result = get_translate_type_by_title("Diagnostic test")
        assert result.tt_title == "Diagnostic test"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_translate_type_by_title("Ghost") is None


class TestAddTranslateType:
    """Tests for add_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_translate_type("Treatment guidelines", 1, 0)
        assert record.tt_title == "Treatment guidelines"
        assert record.tt_lead == 1

    def test_raises_error_if_exists(self, monkeypatch):
        add_translate_type("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_translate_type("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_translate_type("")


class TestAddOrUpdateTranslateType:
    """Tests for add_or_update_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_translate_type("Public health", 1, 0)
        record = add_or_update_translate_type("Public health", 0, 1)
        assert record.tt_lead == 0
        assert record.tt_full == 1
        assert len(list_translate_types()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_or_update_translate_type(" ")


class TestUpdateTranslateType:
    """Tests for update_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        tt = add_translate_type("Global health", 1, 0)
        updated = update_translate_type(tt.tt_id, tt_full=1)
        assert updated.tt_full == 1

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        tt = add_translate_type("No_Change")
        result = update_translate_type(tt.tt_id)
        assert result.tt_title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_translate_type(9999, tt_full=1)


class TestDeleteTranslateType:
    """Tests for delete_translate_type function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        tt = add_translate_type("Pathology report")
        delete_translate_type(tt.tt_id)
        assert get_translate_type(tt.tt_id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_translate_type(9999)


class TestCanTranslateLead:
    """Tests for can_translate_lead function."""

    def test_returns_true_when_tt_lead_is_1(self, monkeypatch):
        """Test that function returns True when tt_lead is 1."""
        add_translate_type("Pharmacology article", tt_lead=1)
        assert can_translate_lead("Pharmacology article") is True

    def test_returns_false_when_tt_lead_is_0(self, monkeypatch):
        """Test that function returns False when tt_lead is 0."""
        add_translate_type("In vivo study", tt_lead=0)
        assert can_translate_lead("In vivo study") is False

    def test_returns_true_when_no_record(self, monkeypatch):
        """Test that function returns True when no record found (default behavior)."""
        assert can_translate_lead("Unknown Title") is True


class TestCanTranslateFull:
    """Tests for can_translate_full function."""

    def test_returns_true_when_tt_full_is_1(self, monkeypatch):
        """Test that function returns True when tt_full is 1."""
        add_translate_type("Expert review", tt_full=1)
        assert can_translate_full("Expert review") is True

    def test_returns_false_when_tt_full_is_0(self, monkeypatch):
        """Test that function returns False when tt_full is 0."""
        add_translate_type("Draft article", tt_full=0)
        assert can_translate_full("Draft article") is False

    def test_returns_false_when_no_record(self, monkeypatch):
        """Test that function returns False when no record found (default behavior)."""
        assert can_translate_full("Unknown Title") is False
