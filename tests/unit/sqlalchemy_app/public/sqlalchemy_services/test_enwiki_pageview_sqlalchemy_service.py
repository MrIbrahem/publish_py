from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models import EnwikiPageviewRecord
from src.sqlalchemy_app.public.sqlalchemy_db.models import _EnwikiPageviewRecord
from src.sqlalchemy_app.public.sqlalchemy_db.services.enwiki_pageview_service import (
    add_enwiki_pageview,
    add_or_update_enwiki_pageview,
    delete_enwiki_pageview,
    get_enwiki_pageview,
    get_enwiki_pageview_by_title,
    get_top_enwiki_pageviews,
    list_enwiki_pageviews,
    update_enwiki_pageview,
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


def test_enwiki_pageview_workflow():
    # Test add
    p = add_enwiki_pageview("test_page", 100)
    assert p.title == "test_page"
    assert p.en_views == 100

    # Test get
    p2 = get_enwiki_pageview(p.id)
    assert p2.title == "test_page"

    # Test get by title
    p3 = get_enwiki_pageview_by_title("test_page")
    assert p3.id == p.id

    # Test list
    all_p = list_enwiki_pageviews()
    assert any(x.title == "test_page" for x in all_p)

    # Test top views
    top = get_top_enwiki_pageviews(1)
    assert top[0].title == "test_page"

    # Test update
    updated = update_enwiki_pageview(p.id, en_views=200)
    assert updated.en_views == 200

    # Test add_or_update
    p4 = add_or_update_enwiki_pageview("test_page", 300)
    assert p4.en_views == 300

    # Test delete
    delete_enwiki_pageview(p.id)
    assert get_enwiki_pageview(p.id) is None
