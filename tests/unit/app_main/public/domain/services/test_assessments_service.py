"""
Unit tests for domain/services/assessment_service.py module.

Tests for assessments service layer which provides cached access to AssessmentsDB.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.public.domain.services.assessment_service import (
    add_assessment,
    add_or_update_assessment,
    delete_assessment,
    get_assessment,
    get_assessment_by_title,
    get_assessments_db,
    list_assessments,
    update_assessment,
)


class TestGetAssessmentsDb:
    """Tests for get_assessments_db function."""

    def test_returns_cached_instance(self, monkeypatch):
        """Test that singleton pattern returns same instance."""
        mock_db = MagicMock()
        monkeypatch.setattr("src.app_main.public.domain.services.assessment_service._ASSESSMENTS_STORE", mock_db)
        monkeypatch.setattr("src.app_main.public.domain.services.assessment_service.has_db_config", lambda: True)

        result = get_assessments_db()

        assert result is mock_db

    def test_raises_when_no_db_config(self, monkeypatch):
        """Test that RuntimeError is raised when DB config is missing."""
        monkeypatch.setattr("src.app_main.public.domain.services.assessment_service._ASSESSMENTS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.assessment_service.has_db_config", lambda: False)

        with pytest.raises(RuntimeError, match="AssessmentsDB requires database configuration"):
            get_assessments_db()

    def test_creates_new_instance_when_cached_is_none(self, monkeypatch):
        """Test that new AssessmentsDB is created when none cached."""
        monkeypatch.setattr("src.app_main.public.domain.services.assessment_service._ASSESSMENTS_STORE", None)
        monkeypatch.setattr("src.app_main.public.domain.services.assessment_service.has_db_config", lambda: True)

        mock_db_instance = MagicMock()
        with patch("src.app_main.public.domain.services.assessment_service.AssessmentsDB") as MockDB:
            MockDB.return_value = mock_db_instance

            result = get_assessments_db()

            assert result is mock_db_instance


class TestListAssessments:
    """Tests for list_assessments function."""

    def test_returns_list_from_store(self, monkeypatch):
        """Test that function returns list from store."""
        mock_store = MagicMock()
        mock_records = [MagicMock(), MagicMock()]
        mock_store.list.return_value = mock_records
        monkeypatch.setattr(
            "src.app_main.public.domain.services.assessment_service.get_assessments_db", lambda: mock_store
        )

        result = list_assessments()

        assert result is mock_records
        mock_store.list.assert_called_once()


class TestGetAssessment:
    """Tests for get_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_id."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_id.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.assessment_service.get_assessments_db", lambda: mock_store
        )

        result = get_assessment(123)

        assert result is mock_record
        mock_store.fetch_by_id.assert_called_once_with(123)


class TestGetAssessmentByTitle:
    """Tests for get_assessment_by_title function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.fetch_by_title."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.fetch_by_title.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.assessment_service.get_assessments_db", lambda: mock_store
        )

        result = get_assessment_by_title("TestPage")

        assert result is mock_record
        mock_store.fetch_by_title.assert_called_once_with("TestPage")


class TestAddAssessment:
    """Tests for add_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.add."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.assessment_service.get_assessments_db", lambda: mock_store
        )

        result = add_assessment("TestPage", importance="High")

        assert result is mock_record
        mock_store.add.assert_called_once_with("TestPage", "High")


class TestAddOrUpdateAssessment:
    """Tests for add_or_update_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.add_or_update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.assessment_service.get_assessments_db", lambda: mock_store
        )

        result = add_or_update_assessment("TestPage", importance="Low")

        assert result is mock_record
        mock_store.add_or_update.assert_called_once_with("TestPage", "Low")


class TestUpdateAssessment:
    """Tests for update_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.update."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.update.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.assessment_service.get_assessments_db", lambda: mock_store
        )

        result = update_assessment(1, importance="Medium")

        assert result is mock_record
        mock_store.update.assert_called_once_with(1, importance="Medium")


class TestDeleteAssessment:
    """Tests for delete_assessment function."""

    def test_delegates_to_store(self, monkeypatch):
        """Test that function delegates to store.delete."""
        mock_store = MagicMock()
        mock_record = MagicMock()
        mock_store.delete.return_value = mock_record
        monkeypatch.setattr(
            "src.app_main.public.domain.services.assessment_service.get_assessments_db", lambda: mock_store
        )

        result = delete_assessment(1)

        assert result is mock_record
        mock_store.delete.assert_called_once_with(1)
