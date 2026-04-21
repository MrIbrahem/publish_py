from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.shared.engine import BaseDb, build_engine, get_session, init_db
from src.sqlalchemy_app.shared.services.report_service import (
    add_report,
    delete_report,
    list_reports,
    query_reports_with_filters,
)
from src.sqlalchemy_app.sqlalchemy_models import ReportRecord, _ReportRecord


def test_report_workflow():
    r = add_report("Malaria", "User:Admin", "en", "Malaria_source", "success", '{"status": "published"}')
    assert r.title == "Malaria"
    assert any(x.title == "Malaria" for x in list_reports())
    filters = {"user": "User:Admin", "lang": "en"}
    assert len(query_reports_with_filters(filters)) >= 1
    delete_report(r.id)
    assert not any(x.id == r.id for x in list_reports())


class TestListReports:
    """Tests for list_reports function."""

    def test_returns_all_reports(self):
        add_report("Tuberculosis", "User:Editor1", "en", "TB_Source", "ok", "{}")
        add_report("Cholera", "User:Editor1", "en", "Cholera_Source", "ok", "{}")
        reports = list_reports()
        assert len(reports) >= 2


class TestAddReport:
    """Tests for add_report function."""

    def test_adds_report_and_returns_record(self):
        record = add_report("Diabetes", "User:Writer", "fr", "Diabète_Source", "ok", "{}")
        assert record.title == "Diabetes"
        assert record.user == "User:Writer"


class TestDeleteReport:
    """Tests for delete_report function."""

    def test_deletes_report(self):
        r = add_report("Influenza", "User:Reporter", "en", "Flu_Source", "ok", "{}")
        delete_report(r.id)
        assert not any(x.id == r.id for x in list_reports())

    def test_raises_lookup_error_when_not_found(self):
        with pytest.raises(LookupError, match="not found"):
            delete_report(99999)


class TestQueryReportsWithFilters:
    """Tests for query_reports_with_filters function."""

    def test_filters_by_user(self):
        add_report("Cancer", "User:Medic", "en", "Cancer_Source", "ok", "{}")
        add_report("Heart Disease", "User:Other", "en", "Heart_Source", "ok", "{}")
        results = query_reports_with_filters({"user": "User:Medic"})
        assert len(results) == 1
        assert results[0].user == "User:Medic"

    def test_filters_by_lang(self):
        add_report("Asthma", "User:Medic", "en", "Asthma_Source", "ok", "{}")
        add_report("Bronchitis", "User:Medic", "fr", "Bronchite_Source", "ok", "{}")
        results = query_reports_with_filters({"lang": "fr"})
        assert len(results) == 1
        assert results[0].lang == "fr"

    def test_handles_all_filter(self):
        add_report("Smallpox", "User:Historian", "en", "Smallpox_Source", "ok", "{}")
        results = query_reports_with_filters({"user": "all"})
        assert len(results) >= 1

    def test_limits_results(self):
        add_report("HIV/AIDS", "User:Researcher", "en", "HIV_Source", "ok", "{}")
        add_report("Polio", "User:Researcher", "en", "Polio_Source", "ok", "{}")
        results = query_reports_with_filters({}, limit=1)
        assert len(results) == 1

    def test_filters_by_year_month(self):
        from datetime import datetime

        with get_session() as session:
            # SQLite current_timestamp is UTC
            session.add(
                _ReportRecord(
                    title="Old Report",
                    user="U",
                    lang="en",
                    sourcetitle="S",
                    result="ok",
                    data="{}",
                    date=datetime(2020, 5, 1),
                )
            )
            session.commit()

        results = query_reports_with_filters({"year": 2020, "month": 5})
        assert len(results) == 1
        assert results[0].title == "Old Report"

    def test_filters_not_empty(self):
        add_report("T1", "U1", "en", "S1", "ok", "{}")
        results = query_reports_with_filters({"title": "not_empty"})
        assert len(results) >= 1

    def test_filters_empty(self):
        # We can't easily add a report with empty title via service because it's not handled there,
        # but we can via manual insert.
        with get_session() as session:
            session.add(_ReportRecord(title="", user="U", lang="en", sourcetitle="S", result="ok", data="{}"))
            session.commit()
        results = query_reports_with_filters({"title": "empty"})
        assert len(results) >= 1
