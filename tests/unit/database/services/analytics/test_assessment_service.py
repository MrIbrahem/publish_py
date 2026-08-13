import pytest

from src.main_app.database.models import AssessmentRecord
from src.main_app.database.services.analytics.assessment_service import AssessmentService
from src.main_app.database.exceptions import RecordNotFoundError


class TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = AssessmentService()


class TestAssessmentService(TestSetup):
    """Tests for AssessmentService class."""

    def test_assessment_workflow(self):
        # Test add
        a = self.service.add_assessment("Diabetes mellitus", "High")
        assert a.title == "Diabetes mellitus"
        assert a.importance == "High"

        # Test get
        a2 = self.service.get_assessment(a.id)
        assert a2 is not None
        assert a2.title == "Diabetes mellitus"

        # Test get by title
        a3 = self.service.get_assessment_by_title("Diabetes mellitus")
        assert a3 is not None
        assert a3.id == a.id

        # Test list
        all_a = self.service.list_assessments()
        assert any(x.title == "Diabetes mellitus" for x in all_a)

        # Test update
        updated = self.service.update_assessment(a.id, importance="Top")
        assert updated.importance == "Top"

        # Test add_or_update
        a4 = self.service.add_or_update_assessment("Diabetes mellitus", "Mid")
        assert a4.importance == "Mid"

        # Test delete
        deleted = self.service.delete_assessment(a.id)
        assert deleted is True
        assert self.service.get_assessment(a.id) is None

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        self.service.add_assessment("Cancer")
        self.service.add_assessment("Hypertension")
        result = self.service.list_assessments()
        assert len(result) >= 2


class TestGetAssessment(TestSetup):
    """Tests for get_assessment method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by ID."""
        a = self.service.add_assessment("Asthma")
        result = self.service.get_assessment(a.id)
        assert isinstance(result, AssessmentRecord)
        assert result.title == "Asthma"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_assessment(9999) is None


class TestGetAssessmentByTitle(TestSetup):
    """Tests for get_assessment_by_title method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method returns record by title."""
        self.service.add_assessment("Stroke")
        result = self.service.get_assessment_by_title("Stroke")
        assert result is not None
        assert result.title == "Stroke"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert self.service.get_assessment_by_title("Ghost") is None


class TestAddAssessment(TestSetup):
    """Tests for add_assessment method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method adds and returns record."""
        record = self.service.add_assessment("Influenza", "Mid")
        assert record.title == "Influenza"
        assert record.importance == "Mid"

    def test_raises_error_if_exists(self, monkeypatch):
        self.service.add_assessment("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            self.service.add_assessment("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_assessment("")


class TestAddOrUpdateAssessment(TestSetup):
    """Tests for add_or_update_assessment method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method upserts record."""
        self.service.add_assessment("Tuberculosis", "Low")
        record = self.service.add_or_update_assessment("Tuberculosis", "High")
        assert record.importance == "High"
        assert len(self.service.list_assessments()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            self.service.add_or_update_assessment(" ")


class TestUpdateAssessment(TestSetup):
    """Tests for update_assessment method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method updates and returns record."""
        a = self.service.add_assessment("Malaria", "Low")
        updated = self.service.update_assessment(a.id, importance="High")
        assert updated.importance == "High"

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        a = self.service.add_assessment("No_Change")
        result = self.service.update_assessment(a.id)
        assert result.title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(RecordNotFoundError, match="not found"):
            self.service.update_assessment(9999, importance="High")


class TestDeleteAssessment(TestSetup):
    """Tests for delete_assessment method."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that method deletes the record."""
        a = self.service.add_assessment("Measles")
        deleted = self.service.delete_assessment(a.id)
        assert deleted is True
        assert self.service.get_assessment(a.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        assert self.service.delete_assessment(9999) is False
