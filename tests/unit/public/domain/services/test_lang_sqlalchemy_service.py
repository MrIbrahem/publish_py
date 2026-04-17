from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models.lang import LangRecord, _LangRecord
from src.app_main.public.domain.sqlalchemy_services.lang_service import (
    add_lang,
    add_or_update_lang,
    delete_lang,
    get_lang,
    get_lang_by_code,
    list_langs,
    update_lang,
)
from src.app_main.shared.db.engine import BaseDb, build_engine, init_db


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


def test_lang_workflow():
    l = add_lang("en", "English", "English")
    assert l.code == "en"
    assert get_lang(l.lang_id).code == "en"
    assert get_lang_by_code("en").lang_id == l.lang_id
    assert any(x.code == "en" for x in list_langs())
    updated = update_lang(l.lang_id, autonym="Eng")
    assert updated.autonym == "Eng"
    l4 = add_or_update_lang("en", "English", "English Lang")
    assert l4.name == "English Lang"
    delete_lang(l.lang_id)
    assert get_lang(l.lang_id) is None
