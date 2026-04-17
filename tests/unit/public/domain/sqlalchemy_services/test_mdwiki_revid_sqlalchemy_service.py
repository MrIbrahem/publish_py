import pytest
from unittest.mock import MagicMock, patch
from src.app_main.shared.sqlalchemy_db.engine import init_db, build_engine, BaseDb
from src.app_main.public.domain.sqlalchemy_services.mdwiki_revid_service import (
    list_mdwiki_revids,
    get_mdwiki_revid_by_title,
    add_mdwiki_revid,
    add_or_update_mdwiki_revid,
    update_mdwiki_revid,
    delete_mdwiki_revid,
    get_revid_for_title
)
from src.app_main.public.domain.models.mdwiki_revid import MdwikiRevidRecord, _MdwikiRevidRecord

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

def test_mdwiki_revid_workflow():
    # Test add
    r = add_mdwiki_revid("test_page", 12345)
    assert r.title == "test_page"
    assert r.revid == 12345

    # Test get by title
    r2 = get_mdwiki_revid_by_title("test_page")
    assert r2.revid == 12345

    # Test get_revid_for_title
    revid = get_revid_for_title("test_page")
    assert revid == 12345

    # Test list
    all_r = list_mdwiki_revids()
    assert any(x.title == "test_page" for x in all_r)

    # Test update
    updated = update_mdwiki_revid("test_page", 67890)
    assert updated.revid == 67890

    # Test add_or_update
    r3 = add_or_update_mdwiki_revid("test_page", 11111)
    assert r3.revid == 11111

    # Test delete
    delete_mdwiki_revid("test_page")
    assert get_mdwiki_revid_by_title("test_page") is None
