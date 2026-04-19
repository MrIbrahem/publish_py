from unittest.mock import MagicMock, patch

import pytest
from src.sqlalchemy_app.public.domain_models import AssessmentRecord
from src.sqlalchemy_app.public.domain.models import _AssessmentRecord
from src.sqlalchemy_app.public.domain.services.assessment_service import (
    add_assessment,
    add_or_update_assessment,
    delete_assessment,
    get_assessment,
    get_assessment_by_title,
    list_assessments,
    update_assessment,
)
from src.sqlalchemy_app.shared.domain.engine import BaseDb, build_engine, init_db


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


def test_assessment_workflow():
    # Test add
    a = add_assessment("test_page", "High")
    assert a.title == "test_page"
    assert a.importance == "High"

    # Test get
    a2 = get_assessment(a.id)
    assert a2.title == "test_page"

    # Test get by title
    a3 = get_assessment_by_title("test_page")
    assert a3.id == a.id

    # Test list
    all_a = list_assessments()
    assert any(x.title == "test_page" for x in all_a)

    # Test update
    updated = update_assessment(a.id, importance="Low")
    assert updated.importance == "Low"

    # Test add_or_update
    a4 = add_or_update_assessment("test_page", "Mid")
    assert a4.importance == "Mid"

    # Test delete
    delete_assessment(a.id)
    assert get_assessment(a.id) is None


class TestListAssessments:
    """Tests for list_assessments function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        add_assessment("p1")
        add_assessment("p2")
        result = list_assessments()
        assert len(result) >= 2


class TestGetAssessment:
    """Tests for get_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by ID."""
        a = add_assessment("p1")
        result = get_assessment(a.id)
        assert isinstance(result, AssessmentRecord)
        assert result.title == "p1"


class TestGetAssessmentByTitle:
    """Tests for get_assessment_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function returns record by title."""
        add_assessment("p1")
        result = get_assessment_by_title("p1")
        assert result.title == "p1"


class TestAddAssessment:
    """Tests for add_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function adds and returns record."""
        record = add_assessment("p1", "High")
        assert record.title == "p1"
        assert record.importance == "High"


class TestAddOrUpdateAssessment:
    """Tests for add_or_update_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function upserts record."""
        add_assessment("p1", "Low")
        record = add_or_update_assessment("p1", "High")
        assert record.importance == "High"
        assert len(list_assessments()) == 1


class TestUpdateAssessment:
    """Tests for update_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function updates and returns record."""
        a = add_assessment("p1", "Low")
        updated = update_assessment(a.id, importance="High")
        assert updated.importance == "High"


class TestDeleteAssessment:
    """Tests for delete_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function deletes the record."""
        a = add_assessment("p1")
        delete_assessment(a.id)
        assert get_assessment(a.id) is None
