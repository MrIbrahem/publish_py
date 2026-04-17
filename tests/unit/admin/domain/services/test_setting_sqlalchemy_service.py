import pytest
from unittest.mock import MagicMock, patch
from src.app_main.shared.db.engine import init_db, build_engine, BaseDb
from src.app_main.admin.domain.sqlalchemy_services.setting_service import (
    list_settings,
    get_setting,
    get_setting_by_key,
    add_setting,
    update_value,
    delete_setting
)
from src.app_main.admin.domain.models.setting import SettingRecord, _SettingRecord

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

def test_setting_workflow():
    s = add_setting("test_key", "Test Title", "string", "test_value")
    assert s.key == "test_key"
    assert get_setting(s.id).key == "test_key"
    assert get_setting_by_key("test_key").id == s.id
    assert any(x.key == "test_key" for x in list_settings())
    updated = update_value(s.id, "new_value")
    assert updated.value == "new_value"
    delete_setting(s.id)
    assert get_setting(s.id) is None
