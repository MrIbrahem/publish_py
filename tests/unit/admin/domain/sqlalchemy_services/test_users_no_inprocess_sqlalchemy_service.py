from unittest.mock import MagicMock, patch

import pytest
from src.app_main.admin.domain.models.users_no_inprocess import UsersNoInprocessRecord, _UsersNoInprocessRecord
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
    rec = add_users_no_inprocess("test_user", 1)
    assert rec.user == "test_user"
    assert get_users_no_inprocess(rec.id).user == "test_user"
    assert get_users_no_inprocess_by_user("test_user").id == rec.id
    assert any(x.user == "test_user" for x in list_users_no_inprocess())
    assert any(x.user == "test_user" for x in list_active_users_no_inprocess())
    updated = update_users_no_inprocess(rec.id, active=0)
    assert updated.active == 0
    assert should_hide_from_inprocess("test_user") is False
    rec4 = add_or_update_users_no_inprocess("test_user", 1)
    assert rec4.active == 1
    delete_users_no_inprocess(rec.id)
    assert get_users_no_inprocess(rec.id) is None
