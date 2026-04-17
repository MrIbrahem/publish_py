from unittest.mock import MagicMock, patch

import pytest
from src.app_main.admin.domain.models.users_no_inprocess import UsersNoInprocessRecord
from src.app_main.admin.domain.sqlalchemy_models.users_no_inprocess import _UsersNoInprocessRecord
from src.app_main.admin.domain.sqlalchemy_services.users_no_inprocess_service import (
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
from src.app_main.shared.sqlalchemy_db.engine import BaseDb, build_engine, init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.app_main.shared.sqlalchemy_db.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_users_no_inprocess_workflow():
    # Test add
    rec = add_users_no_inprocess("test_user", 1)
    assert rec.user == "test_user"
    assert rec.active == 1

    # Test get
    rec2 = get_users_no_inprocess(rec.id)
    assert rec2.user == "test_user"

    # Test get by user
    rec3 = get_users_no_inprocess_by_user("test_user")
    assert rec3.id == rec.id

    # Test list
    all_rec = list_users_no_inprocess()
    assert any(x.user == "test_user" for x in all_rec)

    # Test active
    active = list_active_users_no_inprocess()
    assert any(x.user == "test_user" for x in active)

    # Test update
    updated = update_users_no_inprocess(rec.id, active=0)
    assert updated.active == 0
    assert should_hide_from_inprocess("test_user") is False

    # Test add_or_update
    rec4 = add_or_update_users_no_inprocess("test_user", 1)
    assert rec4.active == 1
    assert should_hide_from_inprocess("test_user") is True

    # Test delete
    delete_users_no_inprocess(rec.id)
    assert get_users_no_inprocess(rec.id) is None
