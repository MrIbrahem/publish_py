from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models import ViewsNewRecord
from src.app_main.public.sqlalchemy_db.models import _ViewsNewRecord
from src.app_main.public.sqlalchemy_db.services.views_new_service import (
    add_or_update_views_new,
    add_views_new,
    delete_views_new,
    get_total_views_for_target,
    get_views_by_target_lang_year,
    get_views_new,
    list_views_by_lang,
    list_views_by_target,
    list_views_new,
    update_views_new,
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


def test_views_new_workflow():
    # Test add
    v = add_views_new("target1", "en", 2023, 1000)
    assert v.target == "target1"
    assert v.views == 1000

    # Test get
    v2 = get_views_new(v.id)
    assert v2.target == "target1"

    # Test get by target, lang, year
    v3 = get_views_by_target_lang_year("target1", "en", 2023)
    assert v3.id == v.id

    # Test list
    all_v = list_views_new()
    assert any(x.target == "target1" for x in all_v)

    # Test list by target/lang
    by_target = list_views_by_target("target1")
    assert len(by_target) >= 1
    by_lang = list_views_by_lang("en")
    assert len(by_lang) >= 1

    # Test update
    updated = update_views_new(v.id, views=2000)
    assert updated.views == 2000

    # Test total views
    total = get_total_views_for_target("target1")
    assert total == 2000

    # Test add_or_update
    v4 = add_or_update_views_new("target1", "en", 2023, 3000)
    assert v4.views == 3000

    # Test delete
    delete_views_new(v.id)
    assert get_views_new(v.id) is None
