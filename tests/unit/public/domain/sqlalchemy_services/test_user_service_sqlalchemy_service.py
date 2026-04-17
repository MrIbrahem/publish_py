from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models.user import UserRecord, _UserRecord
from src.app_main.public.domain.sqlalchemy_services.user_service import (
    add_or_update_user,
    add_user,
    delete_user,
    get_user,
    get_user_by_username,
    list_users,
    list_users_by_group,
    update_user,
    user_exists,
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


def test_user_workflow():
    u = add_user("test_user", "test@example.com", "enwiki", "Editor")
    assert u.username == "test_user"
    assert get_user(u.user_id).username == "test_user"
    assert get_user_by_username("test_user").user_id == u.user_id
    assert any(x.username == "test_user" for x in list_users())
    assert any(x.username == "test_user" for x in list_users_by_group("Editor"))
    updated = update_user(u.user_id, email="new@example.com")
    assert updated.email == "new@example.com"
    assert user_exists("test_user") is True
    u4 = add_or_update_user("test_user", email="final@example.com")
    assert u4.email == "final@example.com"
    delete_user(u.user_id)
    assert get_user(u.user_id) is None
