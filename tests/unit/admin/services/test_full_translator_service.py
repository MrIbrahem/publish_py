from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.admin.services.full_translator_service import (
    add_full_translator,
    add_or_update_full_translator,
    delete_full_translator,
    get_full_translator,
    get_full_translator_by_user,
    is_full_translator,
    list_active_full_translators,
    list_full_translators,
    update_full_translator,
)
from src.sqlalchemy_app.sqlalchemy_models import FullTranslatorRecord


def test_full_translator_workflow():
    # Test add
    ft = add_full_translator("Global_Translator", 1)
    assert ft.user == "Global_Translator"
    assert ft.is_active == 1

    # Test get
    ft2 = get_full_translator(ft.id)
    assert ft2.user == "Global_Translator"

    # Test get by user
    ft3 = get_full_translator_by_user("Global_Translator")
    assert ft3.id == ft.id

    # Test list
    all_ft = list_full_translators()
    assert any(x.user == "Global_Translator" for x in all_ft)

    # Test active
    active = list_active_full_translators()
    assert any(x.user == "Global_Translator" for x in active)

    # Test update
    updated = update_full_translator(ft.id, is_active=0)
    assert updated.is_active == 0
    assert is_full_translator("Global_Translator") is False

    # Test add_or_update
    ft4 = add_or_update_full_translator("Global_Translator", 1)
    assert ft4.is_active == 1
    assert is_full_translator("Global_Translator") is True

    # Test delete
    delete_full_translator(ft.id)
    assert get_full_translator(ft.id) is None


class TestListFullTranslators:
    """Tests for list_full_translators function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_full_translators returns all records."""
        add_full_translator("Translator_Alpha")
        add_full_translator("Translator_Beta")
        result = list_full_translators()
        assert len(result) >= 2


class TestListActiveFullTranslators:
    """Tests for list_active_full_translators function."""

    def test_returns_active_records(self, monkeypatch):
        """Test that list_active_full_translators returns active records."""
        add_full_translator("Active_Trans", is_active=1)
        add_full_translator("Inactive_Trans", is_active=0)
        active = list_active_full_translators()
        assert len(active) == 1
        assert active[0].user == "Active_Trans"


class TestGetFullTranslator:
    """Tests for get_full_translator function."""

    def test_returns_translator_record(self, monkeypatch):
        """Test that function returns a FullTranslatorRecord."""
        ft = add_full_translator("Expert_Linguist")
        result = get_full_translator(ft.id)
        assert isinstance(result, FullTranslatorRecord)
        assert result.user == "Expert_Linguist"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_full_translator(9999) is None


class TestGetFullTranslatorByUser:
    """Tests for get_full_translator_by_user function."""

    def test_returns_translator_by_user(self, monkeypatch):
        """Test that function returns translator by username."""
        add_full_translator("Polyglot_Wiki")
        result = get_full_translator_by_user("Polyglot_Wiki")
        assert result.user == "Polyglot_Wiki"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_full_translator_by_user("Ghost") is None


class TestAddFullTranslator:
    """Tests for add_full_translator function."""

    def test_adds_translator_and_returns_record(self, monkeypatch):
        """Test that add_full_translator adds and returns the record."""
        record = add_full_translator("New_Translator")
        assert record.user == "New_Translator"

    def test_raises_error_if_exists(self, monkeypatch):
        add_full_translator("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_full_translator("Duplicate")

    def test_raises_error_if_no_user(self, monkeypatch):
        with pytest.raises(ValueError, match="User is required"):
            add_full_translator("")


class TestAddOrUpdateFullTranslator:
    """Tests for add_or_update_full_translator function."""

    def test_upserts_translator(self, monkeypatch):
        """Test that add_or_update_full_translator upserts the record."""
        add_full_translator("Sync_Trans", is_active=1)
        record = add_or_update_full_translator("Sync_Trans", is_active=0)
        assert record.is_active == 0
        assert len(list_full_translators()) == 1

    def test_raises_error_if_no_user(self, monkeypatch):
        with pytest.raises(ValueError, match="User is required"):
            add_or_update_full_translator(" ")


class TestUpdateFullTranslator:
    """Tests for update_full_translator function."""

    def test_updates_translator_and_returns_record(self, monkeypatch):
        """Test that update_full_translator updates and returns the record."""
        ft = add_full_translator("Update_Trans", is_active=1)
        updated = update_full_translator(ft.id, is_active=0)
        assert updated.is_active == 0

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        ft = add_full_translator("No_Change")
        result = update_full_translator(ft.id)
        assert result.user == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_full_translator(9999, is_active=0)


class TestDeleteFullTranslator:
    """Tests for delete_full_translator function."""

    def test_deletes_translator(self, monkeypatch):
        """Test that delete_full_translator calls store delete."""
        ft = add_full_translator("Delete_Trans")
        delete_full_translator(ft.id)
        assert get_full_translator(ft.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_full_translator(9999)


class TestIsFullTranslator:
    """Tests for is_full_translator function."""

    def test_returns_true_when_user_is_active_translator(self, monkeypatch):
        """Test that is_full_translator returns True for active translator."""
        add_full_translator("Active_Polyglot", is_active=1)
        assert is_full_translator("Active_Polyglot") is True

    def test_returns_false_when_user_not_translator(self, monkeypatch):
        """Test that is_full_translator returns False when user not found."""
        assert is_full_translator("Ghost_User") is False

    def test_returns_false_when_translator_inactive(self, monkeypatch):
        """Test that is_full_translator returns False for inactive translator."""
        add_full_translator("Inactive_Polyglot", is_active=0)
        assert is_full_translator("Inactive_Polyglot") is False
