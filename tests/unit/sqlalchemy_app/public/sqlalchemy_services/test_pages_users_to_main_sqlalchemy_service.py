from unittest.mock import MagicMock, patch

import pytest
from src.db_models.public_models import PagesUsersToMainRecord
from src.sqlalchemy_app.public.domain.models import _PagesUsersToMainRecord
from src.sqlalchemy_app.public.domain.services.pages_users_to_main_service import (
    add_pages_users_to_main,
    delete_pages_users_to_main,
    get_pages_users_to_main,
    list_pages_users_to_main,
    update_pages_users_to_main,
)
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db("sqlite:///:memory:")
    engine = build_engine("sqlite:///:memory:")
    # Need to create pages_users table first because of FK
    from sqlalchemy import Column, Integer, MetaData, String, Table

    meta = MetaData()
    pages_users = Table("pages_users", meta, Column("id", Integer, primary_key=True), Column("title", String(255)))
    pages_users.create(engine)

    BaseDb.metadata.create_all(engine)
    with patch("src.sqlalchemy_app.shared.domain.engine._SessionFactory") as mock_session_factory:
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        mock_session_factory.return_value = Session()
        yield


def test_pages_users_to_main_workflow():
    from sqlalchemy import text
    from src.sqlalchemy_app.shared.domain.engine import get_session

    with get_session() as session:
        session.execute(text("INSERT INTO pages_users (id, title) VALUES (1, 'test')"))
        session.commit()

    # Test add
    p = add_pages_users_to_main(id=1, new_target="target", new_user="user", new_qid="qid")
    assert p.id == 1
    assert p.new_target == "target"

    # Test get
    p2 = get_pages_users_to_main(1)
    assert p2.new_target == "target"

    # Test list
    all_p = list_pages_users_to_main()
    assert any(x.id == 1 for x in all_p)

    # Test update
    updated = update_pages_users_to_main(1, new_target="new_target")
    assert updated.new_target == "new_target"

    # Test delete
    delete_pages_users_to_main(1)
    assert get_pages_users_to_main(1) is None
