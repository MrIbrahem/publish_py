from unittest.mock import MagicMock, patch

import pytest
from src.db_models.shared_models import UserTokenRecord
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db
from src.sqlalchemy_app.shared.domain.models import _UserTokenRecord
from src.sqlalchemy_app.shared.domain.services.user_token_service import (
    delete_user_token,
    delete_user_token_by_username,
    get_user_token,
    get_user_token_by_username,
    upsert_user_token,
)


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


def test_user_token_workflow():
    upsert_user_token(user_id=1, username="test_user", access_key="key", access_secret="secret")
    t = get_user_token(1)
    assert t.username == "test_user"
    assert get_user_token_by_username("test_user").user_id == 1
    delete_user_token_by_username("test_user")
    assert get_user_token(1) is None
    upsert_user_token(user_id=2, username="user2", access_key="k2", access_secret="s2")
    delete_user_token(2)
    assert get_user_token(2) is None
