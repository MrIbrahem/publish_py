from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.db_models import AssessmentRecord
from src.sqlalchemy_app.sqlalchemy_models import _AssessmentRecord
from src.sqlalchemy_app.public.services.assessment_service import (
    add_assessment,
    add_or_update_assessment,
    delete_assessment,
    get_assessment,
    get_assessment_by_title,
    list_assessments,
    update_assessment,
)


def test_assessment_workflow():
    # Test add
    a = add_assessment("Diabetes mellitus", "High")
    assert a.title == "Diabetes mellitus"
    assert a.importance == "High"

    # Test get
    a2 = get_assessment(a.id)
    assert a2.title == "Diabetes mellitus"

    # Test get by title
    a3 = get_assessment_by_title("Diabetes mellitus")
    assert a3.id == a.id

    # Test list
    all_a = list_assessments()
    assert any(x.title == "Diabetes mellitus" for x in all_a)

    # Test update
    updated = update_assessment(a.id, importance="Top")
    assert updated.importance == "Top"

    # Test add_or_update
    a4 = add_or_update_assessment("Diabetes mellitus", "Mid")
    assert a4.importance == "Mid"

    # Test delete
    delete_assessment(a.id)
    assert get_assessment(a.id) is None


class TestListAssessments:
    """Tests for list_assessments function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_assessment("Cancer")
        add_assessment("Hypertension")
        result = list_assessments()
        assert len(result) >= 2


class TestGetAssessment:
    """Tests for get_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        a = add_assessment("Asthma")
        result = get_assessment(a.id)
        assert isinstance(result, AssessmentRecord)
        assert result.title == "Asthma"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_assessment(9999) is None


class TestGetAssessmentByTitle:
    """Tests for get_assessment_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_assessment("Stroke")
        result = get_assessment_by_title("Stroke")
        assert result.title == "Stroke"

    def test_returns_none_when_not_found(self, monkeypatch):
        assert get_assessment_by_title("Ghost") is None


class TestAddAssessment:
    """Tests for add_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_assessment("Influenza", "Mid")
        assert record.title == "Influenza"
        assert record.importance == "Mid"

    def test_raises_error_if_exists(self, monkeypatch):
        add_assessment("Duplicate")
        with pytest.raises(ValueError, match="already exists"):
            add_assessment("Duplicate")

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_assessment("")


class TestAddOrUpdateAssessment:
    """Tests for add_or_update_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_assessment("Tuberculosis", "Low")
        record = add_or_update_assessment("Tuberculosis", "High")
        assert record.importance == "High"
        assert len(list_assessments()) == 1

    def test_raises_error_if_no_title(self, monkeypatch):
        with pytest.raises(ValueError, match="Title is required"):
            add_or_update_assessment(" ")


class TestUpdateAssessment:
    """Tests for update_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        a = add_assessment("Malaria", "Low")
        updated = update_assessment(a.id, importance="High")
        assert updated.importance == "High"

    def test_returns_record_if_no_kwargs(self, monkeypatch):
        a = add_assessment("No_Change")
        result = update_assessment(a.id)
        assert result.title == "No_Change"

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            update_assessment(9999, importance="High")


class TestDeleteAssessment:
    """Tests for delete_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        a = add_assessment("Measles")
        delete_assessment(a.id)
        assert get_assessment(a.id) is None

    def test_raises_error_if_not_found(self, monkeypatch):
        with pytest.raises(ValueError, match="not found"):
            delete_assessment(9999)
