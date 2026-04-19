from unittest.mock import MagicMock, patch

import pytest
from src.db_models.shared_models import CategoryRecord
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db
from src.sqlalchemy_app.shared.domain.models import _CategoryRecord
from src.sqlalchemy_app.shared.domain.services.category_service import (
    add_category,
    delete_category,
    get_camp_to_cats,
    get_campaign_category,
    list_categories,
    update_category,
)


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_category_workflow():
    c = add_category("test_cat", "Display Name", "test_campaign", "cat2", 1, 1)
    assert c.category == "test_cat"
    assert get_campaign_category("test_campaign").category == "test_cat"
    assert any(x.category == "test_cat" for x in list_categories())
    assert get_camp_to_cats()["test_campaign"] == "test_cat"
    updated = update_category(c.id, "new_title", "new_campaign")
    assert updated.category == "new_title"
    delete_category(c.id)
    assert get_campaign_category("new_campaign") is None
