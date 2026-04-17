import pytest
from unittest.mock import MagicMock, patch
from src.app_main.shared.db.engine import init_db, build_engine, BaseDb
from src.app_main.admin.domain.sqlalchemy_services.language_setting_service import (
    list_language_settings,
    get_language_setting,
    get_language_setting_by_code,
    add_language_setting,
    add_or_update_language_setting,
    update_language_setting,
    delete_language_setting
)
from src.app_main.admin.domain.models.language_setting import LanguageSettingRecord, _LanguageSettingRecord

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

def test_language_setting_workflow():
    ls = add_language_setting("en", 1, 0, 1, 0)
    assert ls.lang_code == "en"
    assert get_language_setting(ls.id).lang_code == "en"
    assert get_language_setting_by_code("en").id == ls.id
    assert any(x.lang_code == "en" for x in list_language_settings())
    updated = update_language_setting(ls.id, move_dots=0)
    assert updated.move_dots == 0
    ls4 = add_or_update_language_setting("en", 1, 1, 1, 1)
    assert ls4.expend == 1
    delete_language_setting(ls.id)
    assert get_language_setting(ls.id) is None
