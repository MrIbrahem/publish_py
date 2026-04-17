from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.domain.models.report import ReportRecord
from src.app_main.shared.domain.sqlalchemy_models.report import _ReportRecord
from src.app_main.shared.domain.sqlalchemy_services.report_service import (
    add_report,
    delete_report,
    list_reports,
    query_reports_with_filters,
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


def test_report_workflow():
    r = add_report("title", "user", "en", "sourcetitle", "success", "data")
    assert r.title == "title"
    assert any(x.title == "title" for x in list_reports())
    filters = {"user": "user", "lang": "en"}
    assert len(query_reports_with_filters(filters)) >= 1
    delete_report(r.id)
    assert not any(x.id == r.id for x in list_reports())
