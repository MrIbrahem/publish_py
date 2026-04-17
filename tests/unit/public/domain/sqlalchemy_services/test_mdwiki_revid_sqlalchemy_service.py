from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models.mdwiki_revid import MdwikiRevidRecord, _MdwikiRevidRecord
from src.app_main.public.domain.sqlalchemy_services.mdwiki_revid_service import (
    add_mdwiki_revid,
    add_or_update_mdwiki_revid,
    delete_mdwiki_revid,
    get_mdwiki_revid_by_title,
    get_revid_for_title,
    list_mdwiki_revids,
    update_mdwiki_revid,
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


def test_mdwiki_revid_workflow():
    r = add_mdwiki_revid("test_page", 12345)
    assert r.title == "test_page"
    assert get_mdwiki_revid_by_title("test_page").revid == 12345
    assert get_revid_for_title("test_page") == 12345
    assert any(x.title == "test_page" for x in list_mdwiki_revids())
    updated = update_mdwiki_revid("test_page", 67890)
    assert updated.revid == 67890
    r3 = add_or_update_mdwiki_revid("test_page", 11111)
    assert r3.revid == 11111
    delete_mdwiki_revid("test_page")
    assert get_mdwiki_revid_by_title("test_page") is None
