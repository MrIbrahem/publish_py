from unittest.mock import MagicMock, patch

import pytest
from src.app_main.admin.domain.models.full_translator import FullTranslatorRecord, _FullTranslatorRecord
from src.app_main.admin.domain.sqlalchemy_services.full_translator_service import (
    add_full_translator,
    add_or_update_full_translator,
    delete_full_translator,
    get_full_translator,
    get_full_translator_by_user,
    is_full_translator,
    list_active_full_translators,
    list_full_translators,
    update_full_translator,
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


def test_full_translator_workflow():
    ft = add_full_translator("test_ft", 1)
    assert ft.user == "test_ft"
    assert ft.active == 1
    assert get_full_translator(ft.id).user == "test_ft"
    assert get_full_translator_by_user("test_ft").id == ft.id
    assert any(x.user == "test_ft" for x in list_full_translators())
    assert any(x.user == "test_ft" for x in list_active_full_translators())
    updated = update_full_translator(ft.id, active=0)
    assert updated.active == 0
    assert is_full_translator("test_ft") is False
    ft4 = add_or_update_full_translator("test_ft", 1)
    assert ft4.active == 1
    delete_full_translator(ft.id)
    assert get_full_translator(ft.id) is None
