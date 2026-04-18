from unittest.mock import MagicMock, patch

import pytest
from src.app_main.admin.domain.admin_models import LanguageSettingRecord
from src.sqlalchemy_app.admin.sqlalchemy_db.models import _LanguageSettingRecord
from src.sqlalchemy_app.admin.sqlalchemy_db.services.language_setting_service import (
    add_language_setting,
    add_or_update_language_setting,
    delete_language_setting,
    get_language_setting,
    get_language_setting_by_code,
    list_language_settings,
    update_language_setting,
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


def test_language_setting_workflow():
    # Test add
    ls = add_language_setting("en", 1, 0, 1, 0)
    assert ls.lang_code == "en"
    assert ls.move_dots == 1

    # Test get
    ls2 = get_language_setting(ls.id)
    assert ls2.lang_code == "en"

    # Test get by code
    ls3 = get_language_setting_by_code("en")
    assert ls3.id == ls.id

    # Test list
    all_ls = list_language_settings()
    assert any(x.lang_code == "en" for x in all_ls)

    # Test update
    updated = update_language_setting(ls.id, move_dots=0)
    assert updated.move_dots == 0

    # Test add_or_update
    ls4 = add_or_update_language_setting("en", 1, 1, 1, 1)
    assert ls4.move_dots == 1
    assert ls4.expend == 1

    # Test delete
    delete_language_setting(ls.id)
    assert get_language_setting(ls.id) is None
