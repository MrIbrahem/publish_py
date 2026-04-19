from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.admin.domain_models import CoordinatorRecord
from src.sqlalchemy_app.admin.domain.models import _CoordinatorRecord
from src.sqlalchemy_app.admin.domain.services.coordinator_service import (
    active_coordinators,
    add_coordinator,
    add_or_update_coordinator,
    delete_coordinator,
    get_coordinator,
    get_coordinator_by_user,
    is_coordinator,
    list_coordinators,
    set_coordinator_active,
    update_coordinator,
)
from src.sqlalchemy_app.shared.domain.engine import init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine

    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_coordinator_workflow():
    # Test add
    c = add_coordinator("test_user", 1)
    assert c.username == "test_user"
    assert c.is_active == 1
    assert c.id is not None

    # Test get
    c2 = get_coordinator(c.id)
    assert c2.username == "test_user"

    # Test get by user
    c3 = get_coordinator_by_user("test_user")
    assert c3.id == c.id

    # Test list
    all_c = list_coordinators()
    assert len(all_c) >= 1
    assert any(x.username == "test_user" for x in all_c)

    # Test active
    active_coordinators.cache_clear()
    active = active_coordinators()
    assert "test_user" in active

    # Test update
    updated = update_coordinator(c.id, is_active=0)
    assert updated.is_active == 0

    active_coordinators.cache_clear()
    assert "test_user" not in active_coordinators()

    # Test is_coordinator
    assert is_coordinator("test_user") is False
    set_coordinator_active(c.id, True)
    assert is_coordinator("test_user") is True

    # Test add_or_update
    c4 = add_or_update_coordinator("test_user", 0)
    assert c4.is_active == 0

    # Test delete
    delete_coordinator(c.id)
    assert get_coordinator(c.id) is None


class TestListCoordinators:
    """Tests for list_coordinators function."""

    def test_returns_list_of_records(self, monkeypatch):
        """Test that list_coordinators returns all records."""
        add_coordinator("u1")
        add_coordinator("u2")
        result = list_coordinators()
        assert len(result) >= 2


class TestListActiveCoordinators:
    """Tests for active_coordinators function."""

    def test_returns_active_usernames(self, monkeypatch):
        """Test that active_coordinators returns active coordinator usernames."""
        active_coordinators.cache_clear()
        add_coordinator("u1", is_active=1)
        add_coordinator("u2", is_active=0)
        active = active_coordinators()
        assert "u1" in active
        assert "u2" not in active


class TestGetCoordinator:
    """Tests for get_coordinator function."""

    def test_returns_coordinator_record(self, monkeypatch):
        """Test that function returns a CoordinatorRecord."""
        c = add_coordinator("u1")
        result = get_coordinator(c.id)
        assert isinstance(result, CoordinatorRecord)
        assert result.username == "u1"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that function returns None when coordinator not found."""
        assert get_coordinator(999) is None


class TestGetCoordinatorByUser:
    """Tests for get_coordinator_by_user function."""

    def test_returns_coordinator_by_user(self, monkeypatch):
        """Test that function returns coordinator by username."""
        add_coordinator("u1")
        result = get_coordinator_by_user("u1")
        assert result.username == "u1"


class TestAddCoordinator:
    """Tests for add_coordinator function."""

    def test_adds_coordinator_and_returns_record(self, monkeypatch):
        """Test that add_coordinator adds and returns the record."""
        record = add_coordinator("u1")
        assert record.username == "u1"


class TestAddOrUpdateCoordinator:
    """Tests for add_or_update_coordinator function."""

    def test_upserts_coordinator(self, monkeypatch):
        """Test that add_or_update_coordinator upserts the record."""
        add_coordinator("u1", is_active=1)
        record = add_or_update_coordinator("u1", is_active=0)
        assert record.is_active == 0
        assert len(list_coordinators()) == 1


class TestUpdateCoordinator:
    """Tests for update_coordinator function."""

    def test_updates_coordinator_and_returns_record(self, monkeypatch):
        """Test that update_coordinator updates and returns the record."""
        c = add_coordinator("u1", is_active=1)
        updated = update_coordinator(c.id, is_active=0)
        assert updated.is_active == 0


class TestDeleteCoordinator:
    """Tests for delete_coordinator function."""

    def test_deletes_coordinator(self, monkeypatch):
        """Test that delete_coordinator calls store delete."""
        c = add_coordinator("u1")
        delete_coordinator(c.id)
        assert get_coordinator(c.id) is None


class TestIsCoordinator:
    """Tests for is_coordinator function."""

    def test_returns_true_when_user_is_active_coordinator(self, monkeypatch):
        """Test that is_coordinator returns True for active coordinator."""
        add_coordinator("u1", is_active=1)
        assert is_coordinator("u1") is True

    def test_returns_false_when_user_not_coordinator(self, monkeypatch):
        """Test that is_coordinator returns False when username not found."""
        assert is_coordinator("ghost") is False

    def test_returns_false_when_coordinator_inactive(self, monkeypatch):
        """Test that is_coordinator returns False for inactive coordinator."""
        add_coordinator("u1", is_active=0)
        assert is_coordinator("u1") is False
