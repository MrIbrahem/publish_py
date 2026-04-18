from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models import LangRecord
from src.app_main.public.sqlalchemy_db.models import _LangRecord
from src.app_main.public.sqlalchemy_db.services.lang_service import (
    add_lang,
    add_or_update_lang,
    delete_lang,
    get_lang,
    get_lang_by_code,
    list_langs,
    update_lang,
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


def test_lang_workflow():
    # Test add
    l = add_lang("en", "English", "English")
    assert l.code == "en"
    assert l.autonym == "English"

    # Test get
    l2 = get_lang(l.lang_id)
    assert l2.code == "en"

    # Test get by code
    l3 = get_lang_by_code("en")
    assert l3.lang_id == l.lang_id

    # Test list
    all_l = list_langs()
    assert any(x.code == "en" for x in all_l)

    # Test update
    updated = update_lang(l.lang_id, autonym="Eng")
    assert updated.autonym == "Eng"

    # Test add_or_update
    l4 = add_or_update_lang("en", "English", "English Lang")
    assert l4.name == "English Lang"

    # Test delete
    delete_lang(l.lang_id)
    assert get_lang(l.lang_id) is None
