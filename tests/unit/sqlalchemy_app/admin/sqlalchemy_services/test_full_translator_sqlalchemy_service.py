from unittest.mock import MagicMock, patch

import pytest
from src.db_models.admin_models import FullTranslatorRecord
from src.sqlalchemy_app.admin.domain.models import _FullTranslatorRecord
from src.sqlalchemy_app.admin.domain.services.full_translator_service import (
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
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_full_translator_workflow():
    # Test add
    ft = add_full_translator("test_ft", 1)
    assert ft.user == "test_ft"
    assert ft.active == 1

    # Test get
    ft2 = get_full_translator(ft.id)
    assert ft2.user == "test_ft"

    # Test get by user
    ft3 = get_full_translator_by_user("test_ft")
    assert ft3.id == ft.id

    # Test list
    all_ft = list_full_translators()
    assert any(x.user == "test_ft" for x in all_ft)

    # Test active
    active = list_active_full_translators()
    assert any(x.user == "test_ft" for x in active)

    # Test update
    updated = update_full_translator(ft.id, active=0)
    assert updated.active == 0
    assert is_full_translator("test_ft") is False

    # Test add_or_update
    ft4 = add_or_update_full_translator("test_ft", 1)
    assert ft4.active == 1
    assert is_full_translator("test_ft") is True

    # Test delete
    delete_full_translator(ft.id)
    assert get_full_translator(ft.id) is None
