from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.models.project import ProjectRecord, _ProjectRecord
from src.app_main.public.domain.sqlalchemy_services.project_service import (
    add_or_update_project,
    add_project,
    delete_project,
    get_project,
    get_project_by_title,
    list_projects,
    update_project,
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


def test_project_workflow():
    p = add_project("test_project")
    assert p.g_title == "test_project"
    assert get_project(p.g_id).g_title == "test_project"
    assert get_project_by_title("test_project").g_id == p.g_id
    assert any(x.g_title == "test_project" for x in list_projects())
    updated = update_project(p.g_id, g_title="new_title")
    assert updated.g_title == "new_title"
    p4 = add_or_update_project("new_title")
    assert p4.g_id == p.g_id
    delete_project(p.g_id)
    assert get_project(p.g_id) is None
