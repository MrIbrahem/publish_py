from unittest.mock import MagicMock, patch

import pytest
from src.app_main.admin.domain.models.coordinator import CoordinatorRecord
from src.app_main.admin.sqlalchemy_db.models.coordinator import _CoordinatorRecord
from src.app_main.admin.sqlalchemy_db.services.coordinator_service import (
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
from src.app_main.shared.sqlalchemy_db.engine import init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    from src.app_main.shared.sqlalchemy_db.engine import BaseDb, build_engine

    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.app_main.shared.sqlalchemy_db.engine._SessionFactory") as mock_session_factory:
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
