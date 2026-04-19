from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.shared.domain_models import ReportRecord
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db
from src.sqlalchemy_app.shared.domain.models import _ReportRecord
from src.sqlalchemy_app.shared.domain.services.report_service import (
    add_report,
    delete_report,
    list_reports,
    query_reports_with_filters,
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


def test_report_workflow():
    r = add_report("title", "user", "en", "sourcetitle", "success", "data")
    assert r.title == "title"
    assert any(x.title == "title" for x in list_reports())
    filters = {"user": "user", "lang": "en"}
    assert len(query_reports_with_filters(filters)) >= 1
    delete_report(r.id)
    assert not any(x.id == r.id for x in list_reports())


class TestListReports:
    """Tests for list_reports function."""

    def test_returns_all_reports(self):
        add_report("t1", "u1", "en", "s1", "ok", "d1")
        add_report("t2", "u1", "en", "s2", "ok", "d2")
        reports = list_reports()
        assert len(reports) >= 2


class TestAddReport:
    """Tests for add_report function."""

    def test_adds_report_and_returns_record(self):
        record = add_report("t1", "u1", "en", "s1", "ok", "d1")
        assert record.title == "t1"
        assert record.user == "u1"


class TestDeleteReport:
    """Tests for delete_report function."""

    def test_deletes_report(self):
        r = add_report("t1", "u1", "en", "s1", "ok", "d1")
        delete_report(r.id)
        assert not any(x.id == r.id for x in list_reports())

    def test_raises_lookup_error_when_not_found(self):
        with pytest.raises(LookupError):
            delete_report(999)


class TestQueryReportsWithFilters:
    """Tests for query_reports_with_filters function."""

    def test_filters_by_user(self):
        add_report("t1", "u1", "en", "s1", "ok", "d1")
        add_report("t2", "u2", "en", "s2", "ok", "d2")
        results = query_reports_with_filters({"user": "u1"})
        assert len(results) == 1
        assert results[0].user == "u1"

    def test_filters_by_lang(self):
        add_report("t1", "u1", "en", "s1", "ok", "d1")
        add_report("t2", "u1", "fr", "s2", "ok", "d2")
        results = query_reports_with_filters({"lang": "fr"})
        assert len(results) == 1
        assert results[0].lang == "fr"

    def test_handles_all_filter(self):
        add_report("t1", "u1", "en", "s1", "ok", "d1")
        results = query_reports_with_filters({"user": "all"})
        assert len(results) >= 1

    def test_limits_results(self):
        add_report("t1", "u1", "en", "s1", "ok", "d1")
        add_report("t2", "u1", "en", "s2", "ok", "d2")
        results = query_reports_with_filters({}, limit=1)
        assert len(results) == 1
