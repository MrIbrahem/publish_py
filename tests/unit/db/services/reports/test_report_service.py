import pytest

from src.main_app.db.models import ReportRecord
from src.main_app.db.services.reports.report_service import (
    ReportService,
)

pytestmark = pytest.mark.unit


class TestReportService:

    def test_report_workflow(self):
        service = ReportService()
        r = service.add_report("Malaria", "User:Admin", "en", "Malaria_source", "success", '{"status": "published"}')
        assert r.title == "Malaria"
        assert any(x.title == "Malaria" for x in service.list_reports())
        filters = {"user": "User:Admin", "lang": "en"}
        assert len(service.query_reports_with_filters(filters)) >= 1
        service.delete(r.id)
        assert not any(x.id == r.id for x in service.list_reports())

    def test_returns_all_reports(self):
        service = ReportService()
        service.add_report("Tuberculosis", "User:Editor1", "en", "TB_Source", "ok", "{}")
        service.add_report("Cholera", "User:Editor1", "en", "Cholera_Source", "ok", "{}")
        reports = service.list_reports()
        assert len(reports) >= 2


class TestAddReport:
    """Tests for add_report function."""

    def test_adds_report_and_returns_record(self):
        service = ReportService()
        record = service.add_report("Diabetes", "User:Writer", "fr", "Diabète_Source", "ok", "{}")
        assert record.title == "Diabetes"
        assert record.user == "User:Writer"


class TestDeleteReport:
    """Tests for delete_report function."""

    def test_deletes_report(self):
        service = ReportService()
        r = service.add_report("Influenza", "User:Reporter", "en", "Flu_Source", "ok", "{}")
        service.delete(r.id)
        assert not any(x.id == r.id for x in service.list_reports())

    def test_raises_lookup_error_when_not_found(self):
        service = ReportService()
        assert service.delete(99999) is False


class TestQueryReportsWithFilters:
    """Tests for query_reports_with_filters function."""

    def test_filters_by_user(self):
        service = ReportService()
        service.add_report("Cancer", "User:Medic", "en", "Cancer_Source", "ok", "{}")
        service.add_report("Heart Disease", "User:Other", "en", "Heart_Source", "ok", "{}")
        results = service.query_reports_with_filters({"user": "User:Medic"})
        assert len(results) == 1
        assert results[0].user == "User:Medic"

    def test_filters_by_lang(self):
        service = ReportService()
        service.add_report("Asthma", "User:Medic", "en", "Asthma_Source", "ok", "{}")
        service.add_report("Bronchitis", "User:Medic", "fr", "Bronchite_Source", "ok", "{}")
        results = service.query_reports_with_filters({"lang": "fr"})
        assert len(results) == 1
        assert results[0].lang == "fr"

    def test_handles_all_filter(self):
        service = ReportService()
        service.add_report("Smallpox", "User:Historian", "en", "Smallpox_Source", "ok", "{}")
        results = service.query_reports_with_filters({"user": "all"})
        assert len(results) >= 1

    def test_limits_results(self):
        service = ReportService()
        service.add_report("HIV/AIDS", "User:Researcher", "en", "HIV_Source", "ok", "{}")
        service.add_report("Polio", "User:Researcher", "en", "Polio_Source", "ok", "{}")
        results = service.query_reports_with_filters({}, limit=1)
        assert len(results) == 1

    def test_filters_by_year_month(self, sqlite_db):
        service = ReportService()
        from datetime import datetime

        sqlite_db.session.add(
            ReportRecord(
                title="Old Report",
                user="U",
                lang="en",
                sourcetitle="S",
                result="ok",
                data="{}",
                date=datetime(2020, 5, 1),
            )
        )
        sqlite_db.session.commit()

        results = service.query_reports_with_filters({"year": 2020, "month": 5})
        assert len(results) == 1
        assert results[0].title == "Old Report"

    def test_filters_not_empty(self):
        service = ReportService()
        service.add_report("T1", "U1", "en", "S1", "ok", "{}")
        results = service.query_reports_with_filters({"title": "not_empty"})
        assert len(results) >= 1

    def test_filters_empty(self, sqlite_db):
        service = ReportService()
        # We can't easily add a report with empty title via service because it's not handled there,
        # but we can via manual insert.
        sqlite_db.session.add(ReportRecord(title="", user="U", lang="en", sourcetitle="S", result="ok", data="{}"))
        sqlite_db.session.commit()
        results = service.query_reports_with_filters({"title": "empty"})
        assert len(results) >= 1
