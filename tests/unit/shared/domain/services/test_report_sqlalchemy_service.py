from unittest.mock import MagicMock, patch

import pytest
from src.db_models.shared_models import ReportRecord
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db
from src.sqlalchemy_app.shared.domain.models import _ReportRecord
from src.sqlalchemy_app.shared.domain.services.report_service import (
    add_report,
    delete_report,
    list_reports,
    query_reports_with_filters,
)





def test_report_workflow():
    r = add_report("title", "user", "en", "sourcetitle", "success", "data")
    assert r.title == "title"
    assert any(x.title == "title" for x in list_reports())
    filters = {"user": "user", "lang": "en"}
    assert len(query_reports_with_filters(filters)) >= 1
    delete_report(r.id)
    assert not any(x.id == r.id for x in list_reports())
