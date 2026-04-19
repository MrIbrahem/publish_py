from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.admin.domain_models import FullTranslatorRecord
from src.sqlalchemy_app.admin.domain.models import _FullTranslatorRecord
from src.sqlalchemy_app.admin.domain.services.full_translator_service import (
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


def test_full_translator_workflow():
    # Test add
    ft = add_full_translator("test_ft", 1)
    assert ft.user == "test_ft"
    assert ft.active == 1

    # Test get
    ft2 = get_full_translator(ft.id)
    assert ft2.user == "test_ft"

    # Test get by user
    ft3 = get_full_translator_by_user("test_ft")
    assert ft3.id == ft.id

    # Test list
    all_ft = list_full_translators()
    assert any(x.user == "test_ft" for x in all_ft)

    # Test active
    active = list_active_full_translators()
    assert any(x.user == "test_ft" for x in active)

    # Test update
    updated = update_full_translator(ft.id, active=0)
    assert updated.active == 0
    assert is_full_translator("test_ft") is False

    # Test add_or_update
    ft4 = add_or_update_full_translator("test_ft", 1)
    assert ft4.active == 1
    assert is_full_translator("test_ft") is True

    # Test delete
    delete_full_translator(ft.id)
    assert get_full_translator(ft.id) is None


class TestListFullTranslators:
    """Tests for list_full_translators function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_full_translators returns all records."""
        add_full_translator("u1")
        add_full_translator("u2")
        result = list_full_translators()
        assert len(result) >= 2


class TestListActiveFullTranslators:
    """Tests for list_active_full_translators function."""

    def test_returns_active_records(self, monkeypatch):
        """Test that list_active_full_translators returns active records."""
        add_full_translator("u1", active=1)
        add_full_translator("u2", active=0)
        active = list_active_full_translators()
        assert len(active) == 1
        assert active[0].user == "u1"


class TestGetFullTranslator:
    """Tests for get_full_translator function."""

    def test_returns_translator_record(self, monkeypatch):
        """Test that function returns a FullTranslatorRecord."""
        ft = add_full_translator("u1")
        result = get_full_translator(ft.id)
        assert isinstance(result, FullTranslatorRecord)
        assert result.user == "u1"


class TestGetFullTranslatorByUser:
    """Tests for get_full_translator_by_user function."""

    def test_returns_translator_by_user(self, monkeypatch):
        """Test that function returns translator by username."""
        add_full_translator("u1")
        result = get_full_translator_by_user("u1")
        assert result.user == "u1"


class TestAddFullTranslator:
    """Tests for add_full_translator function."""

    def test_adds_translator_and_returns_record(self, monkeypatch):
        """Test that add_full_translator adds and returns the record."""
        record = add_full_translator("u1")
        assert record.user == "u1"


class TestAddOrUpdateFullTranslator:
    """Tests for add_or_update_full_translator function."""

    def test_upserts_translator(self, monkeypatch):
        """Test that add_or_update_full_translator upserts the record."""
        add_full_translator("u1", active=1)
        record = add_or_update_full_translator("u1", active=0)
        assert record.active == 0
        assert len(list_full_translators()) == 1


class TestUpdateFullTranslator:
    """Tests for update_full_translator function."""

    def test_updates_translator_and_returns_record(self, monkeypatch):
        """Test that update_full_translator updates and returns the record."""
        ft = add_full_translator("u1", active=1)
        updated = update_full_translator(ft.id, active=0)
        assert updated.active == 0


class TestDeleteFullTranslator:
    """Tests for delete_full_translator function."""

    def test_deletes_translator(self, monkeypatch):
        """Test that delete_full_translator calls store delete."""
        ft = add_full_translator("u1")
        delete_full_translator(ft.id)
        assert get_full_translator(ft.id) is None


class TestIsFullTranslator:
    """Tests for is_full_translator function."""

    def test_returns_true_when_user_is_active_translator(self, monkeypatch):
        """Test that is_full_translator returns True for active translator."""
        add_full_translator("u1", active=1)
        assert is_full_translator("u1") is True

    def test_returns_false_when_user_not_translator(self, monkeypatch):
        """Test that is_full_translator returns False when user not found."""
        assert is_full_translator("ghost") is False

    def test_returns_false_when_translator_inactive(self, monkeypatch):
        """Test that is_full_translator returns False for inactive translator."""
        add_full_translator("u1", active=0)
        assert is_full_translator("u1") is False
