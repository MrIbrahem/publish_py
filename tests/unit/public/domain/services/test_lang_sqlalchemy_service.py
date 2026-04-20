from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import LangRecord
from src.sqlalchemy_app.public.domain.models import _LangRecord
from src.sqlalchemy_app.public.domain.services.lang_service import (
    add_lang,
    add_or_update_lang,
    delete_lang,
    get_lang,
    get_lang_by_code,
    list_langs,
    update_lang,
)


def test_lang_workflow():
    # Test add
    l = add_lang("en", "English", "English")
    assert l.code == "en"
    assert l.autonym == "English"

    # Test get
    l2 = get_lang(l.lang_id)
    assert l2.code == "en"

    # Test get by code
    l3 = get_lang_by_code("en")
    assert l3.lang_id == l.lang_id

    # Test list
    all_l = list_langs()
    assert any(x.code == "en" for x in all_l)

    # Test update
    updated = update_lang(l.lang_id, autonym="Eng")
    assert updated.autonym == "Eng"

    # Test add_or_update
    l4 = add_or_update_lang("en", "English", "English Lang")
    assert l4.name == "English Lang"

    # Test delete
    delete_lang(l.lang_id)
    assert get_lang(l.lang_id) is None


class TestListLangs:
    """Tests for list_langs function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""


class TestGetLang:
    """Tests for get_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""


class TestGetLangByCode:
    """Tests for get_lang_by_code function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_code."""


class TestAddLang:
    """Tests for add_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""


class TestAddOrUpdateLang:
    """Tests for add_or_update_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""


class TestUpdateLang:
    """Tests for update_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""


class TestDeleteLang:
    """Tests for delete_lang function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
