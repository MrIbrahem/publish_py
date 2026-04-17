import pytest
from unittest.mock import MagicMock, patch
from src.app_main.shared.db.engine import init_db, build_engine, BaseDb
from src.app_main.shared.domain.sqlalchemy_services.user_token_service import (
    upsert_user_token,
    get_user_token,
    delete_user_token,
    get_user_token_by_username,
    delete_user_token_by_username
)
from src.app_main.shared.domain.models.user_token import UserTokenRecord, _UserTokenRecord

@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.app_main.shared.db.engine._SessionFactory") as mock_session_factory:
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
