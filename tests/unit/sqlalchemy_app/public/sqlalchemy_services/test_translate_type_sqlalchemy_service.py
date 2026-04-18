from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import TranslateTypeRecord
from src.sqlalchemy_app.public.sqlalchemy_db.models import _TranslateTypeRecord
from src.sqlalchemy_app.public.sqlalchemy_db.services.translate_type_service import (
    add_or_update_translate_type,
    add_translate_type,
    can_translate_full,
    can_translate_lead,
    delete_translate_type,
    get_translate_type,
    get_translate_type_by_title,
    list_full_enabled_types,
    list_lead_enabled_types,
    list_translate_types,
    update_translate_type,
)
from src.sqlalchemy_app.shared.sqlalchemy_db.engine import BaseDb, build_engine, init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.sqlalchemy_db.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_translate_type_workflow():
    # Test add
    tt = add_translate_type("test_type", 1, 0)
    assert tt.tt_title == "test_type"
    assert tt.tt_lead == 1

    # Test get
    tt2 = get_translate_type(tt.tt_id)
    assert tt2.tt_title == "test_type"

    # Test get by title
    tt3 = get_translate_type_by_title("test_type")
    assert tt3.tt_id == tt.tt_id

    # Test list
    all_tt = list_translate_types()
    assert any(x.tt_title == "test_type" for x in all_tt)

    # Test enabled lists
    leads = list_lead_enabled_types()
    assert any(x.tt_title == "test_type" for x in leads)
    fulls = list_full_enabled_types()
    assert not any(x.tt_title == "test_type" for x in fulls)

    # Test can_translate
    assert can_translate_lead("test_type") is True
    assert can_translate_full("test_type") is False

    # Test update
    updated = update_translate_type(tt.tt_id, tt_full=1)
    assert updated.tt_full == 1
    assert can_translate_full("test_type") is True

    # Test add_or_update
    tt4 = add_or_update_translate_type("test_type", 0, 1)
    assert tt4.tt_lead == 0

    # Test delete
    delete_translate_type(tt.tt_id)
    assert get_translate_type(tt.tt_id) is None
