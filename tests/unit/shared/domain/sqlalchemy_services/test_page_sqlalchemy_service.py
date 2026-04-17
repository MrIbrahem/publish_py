from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.domain.models.page import PageRecord
from src.app_main.shared.domain.sqlalchemy_models.page import _PageRecord
from src.app_main.shared.domain.sqlalchemy_services.page_service import (
    add_or_update_page,
    add_page,
    delete_page,
    find_exists_or_update,
    insert_page_target,
    list_pages,
    update_page,
)
from src.app_main.shared.sqlalchemy_db.engine import BaseDb, build_engine, get_session, init_db


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


def test_page_workflow():
    p = add_page("test_page", "target_file")
    assert p.title == "test_page"
    assert any(x.title == "test_page" for x in list_pages())
    updated = update_page(p.id, "new_title", "new_target")
    assert updated.title == "new_title"
    p2 = add_or_update_page("new_title", "final_target")
    assert p2.target == "final_target"
    with get_session() as session:
        orm_p = session.query(_PageRecord).filter(_PageRecord.id == p.id).first()
        orm_p.lang = "en"
        orm_p.user = "user1"
        orm_p.target = ""
        session.commit()
    assert find_exists_or_update("new_title", "en", "user1", "found_target") is True
    success = insert_page_target("new_p", "lead", "cat", "fr", "user2", "target_fr", "pages")
    assert success is True
    delete_page(p.id)
    assert not any(x.id == p.id for x in list_pages())
