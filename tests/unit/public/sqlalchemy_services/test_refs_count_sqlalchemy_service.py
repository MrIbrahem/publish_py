from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models.refs_count import RefsCountRecord
from src.app_main.public.domain.sqlalchemy_models.refs_count import _RefsCountRecord
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
    # Test add
    r = add_refs_count("test_page", 10, 50)
    assert r.r_title == "test_page"
    assert r.r_lead_refs == 10

    # Test get
    r2 = get_refs_count(r.r_id)
    assert r2.r_title == "test_page"

    # Test get by title
    r3 = get_refs_count_by_title("test_page")
    assert r3.r_id == r.r_id

    # Test get_ref_counts_for_title
    lead, all_refs = get_ref_counts_for_title("test_page")
    assert lead == 10
    assert all_refs == 50

    # Test list
    all_r = list_refs_counts()
    assert any(x.r_title == "test_page" for x in all_r)

    # Test update
    updated = update_refs_count(r.r_id, r_lead_refs=20)
    assert updated.r_lead_refs == 20

    # Test add_or_update
    r4 = add_or_update_refs_count("test_page", 30, 60)
    assert r4.r_lead_refs == 30

    # Test delete
    delete_refs_count(r.r_id)
    assert get_refs_count(r.r_id) is None
