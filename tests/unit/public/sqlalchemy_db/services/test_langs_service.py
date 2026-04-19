"""
Unit tests for domain/services/lang_service.py module.

Tests for langs service layer which provides cached access to LangsDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.lang_service import (
    add_lang,
    add_or_update_lang,
    delete_lang,
    get_lang,
    get_lang_by_code,
    get_langs_db,
    list_langs,
    update_lang,
)


class TestGetLangsDb:
    """Tests for get_langs_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new LangsDB is created when none cached."""


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
