import pytest
from unittest.mock import MagicMock, patch
from src.app_main.shared.db.engine import init_db, build_engine, BaseDb
from src.app_main.public.domain.sqlalchemy_services.views_new_service import (
    list_views_new,
    list_views_by_target,
    list_views_by_lang,
    get_views_new,
    get_views_by_target_lang_year,
    add_views_new,
    add_or_update_views_new,
    update_views_new,
    delete_views_new,
    get_total_views_for_target
)
from src.app_main.public.domain.models.views_new import ViewsNewRecord, _ViewsNewRecord

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

def test_views_new_workflow():
    v = add_views_new("target1", "en", 2023, 1000)
    assert v.target == "target1"
    assert get_views_new(v.id).target == "target1"
    assert get_views_by_target_lang_year("target1", "en", 2023).id == v.id
    assert any(x.target == "target1" for x in list_views_new())
    assert len(list_views_by_target("target1")) >= 1
    assert len(list_views_by_lang("en")) >= 1
    updated = update_views_new(v.id, views=2000)
    assert updated.views == 2000
    assert get_total_views_for_target("target1") == 2000
    v4 = add_or_update_views_new("target1", "en", 2023, 3000)
    assert v4.views == 3000
    delete_views_new(v.id)
    assert get_views_new(v.id) is None
