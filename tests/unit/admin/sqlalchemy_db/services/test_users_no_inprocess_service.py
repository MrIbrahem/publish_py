"""
Unit tests for admin/domain/services/users_no_inprocess_service.py module.

Tests for users_no_inprocess service layer which provides cached access to UsersNoInprocessDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.admin.domain.services.users_no_inprocess_service import (
    add_or_update_users_no_inprocess,
    add_users_no_inprocess,
    delete_users_no_inprocess,
    get_users_no_inprocess,
    get_users_no_inprocess_by_user,
    list_active_users_no_inprocess,
    list_users_no_inprocess,
    should_hide_from_inprocess,
    update_users_no_inprocess,
)


class TestGetUsersNoInprocessDb:
    """Tests for get_users_no_inprocess_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""










    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""










    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new UsersNoInprocessDB is created when none cached."""














class TestListUsersNoInprocess:
    """Tests for list_users_no_inprocess function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""














class TestListActiveUsersNoInprocess:
    """Tests for list_active_users_no_inprocess function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns active records from store."""














class TestGetUsersNoInprocess:
    """Tests for get_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""














class TestGetUsersNoInprocessByUser:
    """Tests for get_users_no_inprocess_by_user function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_user."""














class TestAddUsersNoInprocess:
    """Tests for add_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""














class TestAddOrUpdateUsersNoInprocess:
    """Tests for add_or_update_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""














class TestUpdateUsersNoInprocess:
    """Tests for update_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""














class TestDeleteUsersNoInprocess:
    """Tests for delete_users_no_inprocess function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""














class TestShouldHideFromInprocess:
    """Tests for should_hide_from_inprocess function."""

    def test_returns_true_when_record_exists_and_active(self, monkeypatch):
        """Test that function returns True when record exists and is active."""













    def test_returns_false_when_record_exists_but_inactive(self, monkeypatch):
        """Test that function returns False when record exists but is inactive."""













    def test_returns_false_when_no_record(self, monkeypatch):
        """Test that function returns False when no record found."""










