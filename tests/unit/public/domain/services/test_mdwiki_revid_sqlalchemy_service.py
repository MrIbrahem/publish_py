from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import MdwikiRevidRecord
from src.sqlalchemy_app.public.domain.models import _MdwikiRevidRecord
from src.sqlalchemy_app.public.domain.services.mdwiki_revid_service import (
    add_mdwiki_revid,
    add_or_update_mdwiki_revid,
    delete_mdwiki_revid,
    get_mdwiki_revid_by_title,
    get_revid_for_title,
    list_mdwiki_revids,
    update_mdwiki_revid,
)


def test_mdwiki_revid_workflow():
    # Test add
    r = add_mdwiki_revid("Cell biology", 1234567)
    assert r.title == "Cell biology"
    assert r.revid == 1234567

    # Test get by title
    r2 = get_mdwiki_revid_by_title("Cell biology")
    assert r2.revid == 1234567

    # Test get_revid_for_title
    revid = get_revid_for_title("Cell biology")
    assert revid == 1234567

    # Test list
    all_r = list_mdwiki_revids()
    assert any(x.title == "Cell biology" for x in all_r)

    # Test update
    updated = update_mdwiki_revid("Cell biology", 7654321)
    assert updated.revid == 7654321

    # Test add_or_update
    r3 = add_or_update_mdwiki_revid("Cell biology", 9999999)
    assert r3.revid == 9999999

    # Test delete
    delete_mdwiki_revid("Cell biology")
    assert get_mdwiki_revid_by_title("Cell biology") is None


class TestListMdwikiRevids:
    """Tests for list_mdwiki_revids function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_mdwiki_revid("Vaccine", 1010101)
        add_mdwiki_revid("Antibiotics", 2020202)
        result = list_mdwiki_revids()
        assert len(result) >= 2


class TestGetMdwikiRevidByTitle:
    """Tests for get_mdwiki_revid_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_mdwiki_revid("Aspirin", 3030303)
        result = get_mdwiki_revid_by_title("Aspirin")
        assert result.revid == 3030303

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_mdwiki_revid_by_title("Ghost") is None


class TestAddMdwikiRevid:
    """Tests for add_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_mdwiki_revid("Penicillin", 4040404)
        assert record.title == "Penicillin"
        assert record.revid == 4040404

    def test_raises_error_if_exists(self, monkeypatch):
        add_mdwiki_revid("Duplicate", 1)
        with pytest.raises(ValueError, match="already exists"):
            add_mdwiki_revid("Duplicate", 2)

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_mdwiki_revid("", 123)


class TestAddOrUpdateMdwikiRevid:
    """Tests for add_or_update_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_mdwiki_revid("Insulin", 5050505)
        record = add_or_update_mdwiki_revid("Insulin", 6060606)
        assert record.revid == 6060606
        assert len(list_mdwiki_revids()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_or_update_mdwiki_revid(" ", 123)


class TestUpdateMdwikiRevid:
    """Tests for update_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        add_mdwiki_revid("Paracetamol", 7070707)
        updated = update_mdwiki_revid("Paracetamol", 8080808)
        assert updated.revid == 8080808

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_mdwiki_revid("Ghost", 123)


class TestDeleteMdwikiRevid:
    """Tests for delete_mdwiki_revid function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        add_mdwiki_revid("Ibuprofen", 9090909)
        delete_mdwiki_revid("Ibuprofen")
        assert get_mdwiki_revid_by_title("Ibuprofen") is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_mdwiki_revid("Ghost")


class TestGetRevidForTitle:
    """Tests for get_revid_for_title function."""

    def test_returns_revid_when_record_exists(self, monkeypatch):
        """Test that function returns revid when record found."""
        add_mdwiki_revid("Morphine", 1112223)
        assert get_revid_for_title("Morphine") == 1112223

    def test_returns_none_when_record_not_found(self, monkeypatch):
        """Test that function returns None when record not found."""
        assert get_revid_for_title("Ghost_Article") is None
