import pytest
from unittest.mock import MagicMock, patch
from src.app_main.shared.db.engine import init_db, build_engine, BaseDb
from src.app_main.public.domain.sqlalchemy_services.translate_type_service import (
    list_translate_types,
    list_lead_enabled_types,
    list_full_enabled_types,
    get_translate_type,
    get_translate_type_by_title,
    add_translate_type,
    add_or_update_translate_type,
    update_translate_type,
    delete_translate_type,
    can_translate_lead,
    can_translate_full
)
from src.app_main.public.domain.models.translate_type import TranslateTypeRecord, _TranslateTypeRecord

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

def test_translate_type_workflow():
    tt = add_translate_type("test_type", 1, 0)
    assert tt.tt_title == "test_type"
    assert get_translate_type(tt.tt_id).tt_title == "test_type"
    assert get_translate_type_by_title("test_type").tt_id == tt.tt_id
    assert any(x.tt_title == "test_type" for x in list_translate_types())
    assert any(x.tt_title == "test_type" for x in list_lead_enabled_types())
    assert can_translate_lead("test_type") is True
    assert can_translate_full("test_type") is False
    updated = update_translate_type(tt.tt_id, tt_full=1)
    assert updated.tt_full == 1
    tt4 = add_or_update_translate_type("test_type", 0, 1)
    assert tt4.tt_lead == 0
    delete_translate_type(tt.tt_id)
    assert get_translate_type(tt.tt_id) is None
