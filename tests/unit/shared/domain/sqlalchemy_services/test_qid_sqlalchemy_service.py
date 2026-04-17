from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.domain.models.qid import QidRecord, _QidRecord
from src.app_main.shared.domain.sqlalchemy_services.qid_service import (
    add_qid,
    delete_qid,
    get_page_qid,
    get_title_to_qid,
    list_qids,
    update_qid,
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


def test_qid_workflow():
    q = add_qid("test_page", "Q123")
    assert q.title == "test_page"
    assert get_page_qid("test_page").qid == "Q123"
    assert any(x.title == "test_page" for x in list_qids())
    assert get_title_to_qid()["test_page"] == "Q123"
    updated = update_qid(q.id, "new_title", "Q456")
    assert updated.qid == "Q456"
    delete_qid(q.id)
    assert get_page_qid("new_title") is None
