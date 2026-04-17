from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models.enwiki_pageview import EnwikiPageviewRecord, _EnwikiPageviewRecord
from src.app_main.public.domain.sqlalchemy_services.enwiki_pageview_service import (
    add_enwiki_pageview,
    add_or_update_enwiki_pageview,
    delete_enwiki_pageview,
    get_enwiki_pageview,
    get_enwiki_pageview_by_title,
    get_top_enwiki_pageviews,
    list_enwiki_pageviews,
    update_enwiki_pageview,
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


def test_enwiki_pageview_workflow():
    p = add_enwiki_pageview("test_page", 100)
    assert p.title == "test_page"
    assert get_enwiki_pageview(p.id).title == "test_page"
    assert get_enwiki_pageview_by_title("test_page").id == p.id
    assert any(x.title == "test_page" for x in list_enwiki_pageviews())
    assert get_top_enwiki_pageviews(1)[0].title == "test_page"
    updated = update_enwiki_pageview(p.id, en_views=200)
    assert updated.en_views == 200
    p4 = add_or_update_enwiki_pageview("test_page", 300)
    assert p4.en_views == 300
    delete_enwiki_pageview(p.id)
    assert get_enwiki_pageview(p.id) is None
