from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models.refs_count import RefsCountRecord, _RefsCountRecord
from src.app_main.public.domain.sqlalchemy_services.refs_count_service import (
    add_or_update_refs_count,
    add_refs_count,
    delete_refs_count,
    get_ref_counts_for_title,
    get_refs_count,
    get_refs_count_by_title,
    list_refs_counts,
    update_refs_count,
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


def test_refs_count_workflow():
    r = add_refs_count("test_page", 10, 50)
    assert r.r_title == "test_page"
    assert get_refs_count(r.r_id).r_title == "test_page"
    assert get_refs_count_by_title("test_page").r_id == r.r_id
    lead, all_refs = get_ref_counts_for_title("test_page")
    assert lead == 10
    assert any(x.r_title == "test_page" for x in list_refs_counts())
    updated = update_refs_count(r.r_id, r_lead_refs=20)
    assert updated.r_lead_refs == 20
    r4 = add_or_update_refs_count("test_page", 30, 60)
    assert r4.r_lead_refs == 30
    delete_refs_count(r.r_id)
    assert get_refs_count(r.r_id) is None
