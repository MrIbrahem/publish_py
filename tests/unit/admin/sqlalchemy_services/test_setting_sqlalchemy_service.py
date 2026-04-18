from unittest.mock import MagicMock, patch

import pytest
# from src.app_main.admin.domain.models import SettingRecord
# from src.app_main.admin.sqlalchemy_db.models import _SettingRecord
from src.app_main.admin.sqlalchemy_db.services.setting_service import (
    add_setting,
    delete_setting,
    get_setting,
    get_setting_by_key,
    list_settings,
    update_value,
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


def test_setting_workflow():
    # Test add
    s = add_setting("test_key", "Test Title", "string", "test_value")
    assert s.key == "test_key"
    assert s.value == "test_value"

    # Test get
    s2 = get_setting(s.id)
    assert s2.key == "test_key"

    # Test get by key
    s3 = get_setting_by_key("test_key")
    assert s3.id == s.id

    # Test list
    all_s = list_settings()
    assert any(x.key == "test_key" for x in all_s)

    # Test update
    updated = update_value(s.id, "new_value")
    assert updated.value == "new_value"

    # Test delete
    delete_setting(s.id)
    assert get_setting(s.id) is None
