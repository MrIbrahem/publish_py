from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models import ProjectRecord
from src.sqlalchemy_app.public.sqlalchemy_db.models import _ProjectRecord
from src.sqlalchemy_app.public.sqlalchemy_db.services.project_service import (
    add_or_update_project,
    add_project,
    delete_project,
    get_project,
    get_project_by_title,
    list_projects,
    update_project,
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


def test_project_workflow():
    # Test add
    p = add_project("test_project")
    assert p.g_title == "test_project"

    # Test get
    p2 = get_project(p.g_id)
    assert p2.g_title == "test_project"

    # Test get by title
    p3 = get_project_by_title("test_project")
    assert p3.g_id == p.g_id

    # Test list
    all_p = list_projects()
    assert any(x.g_title == "test_project" for x in all_p)

    # Test update
    updated = update_project(p.g_id, g_title="new_title")
    assert updated.g_title == "new_title"

    # Test add_or_update
    p4 = add_or_update_project("new_title")
    assert p4.g_id == p.g_id

    # Test delete
    delete_project(p.g_id)
    assert get_project(p.g_id) is None
