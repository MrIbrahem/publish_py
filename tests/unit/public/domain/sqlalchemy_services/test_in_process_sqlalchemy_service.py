import pytest
from unittest.mock import MagicMock, patch
from src.app_main.shared.sqlalchemy_db.engine import init_db, build_engine, BaseDb
from src.app_main.public.domain.sqlalchemy_services.in_process_service import (
    list_in_process,
    list_in_process_by_user,
    list_in_process_by_lang,
    get_in_process,
    get_in_process_by_title_user_lang,
    add_in_process,
    update_in_process,
    delete_in_process,
    delete_in_process_by_title_user_lang,
    is_in_process
)
from src.app_main.public.domain.models.in_process import InProcessRecord, _InProcessRecord

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

def test_in_process_workflow():
    # Test add
    ip = add_in_process("test_title", "test_user", "en", "RTT", "lead", 100)
    assert ip.title == "test_title"
    assert ip.user == "test_user"

    # Test get
    ip2 = get_in_process(ip.id)
    assert ip2.title == "test_title"

    # Test get by multiple keys
    ip3 = get_in_process_by_title_user_lang("test_title", "test_user", "en")
    assert ip3.id == ip.id

    # Test list
    all_ip = list_in_process()
    assert any(x.title == "test_title" for x in all_ip)

    # Test list by user/lang
    by_user = list_in_process_by_user("test_user")
    assert len(by_user) >= 1
    by_lang = list_in_process_by_lang("en")
    assert len(by_lang) >= 1

    # Test is_in_process
    assert is_in_process("test_title", "test_user", "en") is True

    # Test update
    updated = update_in_process(ip.id, word=200)
    assert updated.word == 200

    # Test delete by title/user/lang
    success = delete_in_process_by_title_user_lang("test_title", "test_user", "en")
    assert success is True
    assert get_in_process(ip.id) is None

    # Test delete by ID
    ip_new = add_in_process("new", "new_user", "fr")
    delete_in_process(ip_new.id)
    assert get_in_process(ip_new.id) is None
