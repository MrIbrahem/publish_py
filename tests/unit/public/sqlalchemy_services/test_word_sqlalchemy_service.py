from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models import WordRecord
from src.app_main.public.sqlalchemy_db.models import _WordRecord
from src.app_main.public.sqlalchemy_db.services.word_service import (
    add_or_update_word,
    add_word,
    delete_word,
    get_word,
    get_word_by_title,
    get_word_counts_for_title,
    list_words,
    update_word,
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


def test_word_workflow():
    # Test add
    w = add_word("test_page", 100, 500)
    assert w.w_title == "test_page"
    assert w.w_lead_words == 100

    # Test get
    w2 = get_word(w.w_id)
    assert w2.w_title == "test_page"

    # Test get by title
    w3 = get_word_by_title("test_page")
    assert w3.w_id == w.w_id

    # Test get_word_counts_for_title
    lead, all_words = get_word_counts_for_title("test_page")
    assert lead == 100
    assert all_words == 500

    # Test list
    all_w = list_words()
    assert any(x.w_title == "test_page" for x in all_w)

    # Test update
    updated = update_word(w.w_id, w_lead_words=150)
    assert updated.w_lead_words == 150

    # Test add_or_update
    w4 = add_or_update_word("test_page", 200, 600)
    assert w4.w_lead_words == 200

    # Test delete
    delete_word(w.w_id)
    assert get_word(w.w_id) is None
