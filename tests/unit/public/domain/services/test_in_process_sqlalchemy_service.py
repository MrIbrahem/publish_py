from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models.in_process import InProcessRecord, _InProcessRecord
from src.app_main.public.domain.sqlalchemy_services.in_process_service import (
    add_in_process,
    delete_in_process,
    delete_in_process_by_title_user_lang,
    get_in_process,
    get_in_process_by_title_user_lang,
    is_in_process,
    list_in_process,
    list_in_process_by_lang,
    list_in_process_by_user,
    update_in_process,
)
from src.app_main.shared.db.engine import BaseDb, build_engine, init_db


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


def test_in_process_workflow():
    ip = add_in_process("test_title", "test_user", "en", "RTT", "lead", 100)
    assert ip.title == "test_title"
    assert get_in_process(ip.id).title == "test_title"
    assert get_in_process_by_title_user_lang("test_title", "test_user", "en").id == ip.id
    assert any(x.title == "test_title" for x in list_in_process())
    assert len(list_in_process_by_user("test_user")) >= 1
    assert len(list_in_process_by_lang("en")) >= 1
    assert is_in_process("test_title", "test_user", "en") is True
    updated = update_in_process(ip.id, word=200)
    assert updated.word == 200
    success = delete_in_process_by_title_user_lang("test_title", "test_user", "en")
    assert success is True
    assert get_in_process(ip.id) is None
