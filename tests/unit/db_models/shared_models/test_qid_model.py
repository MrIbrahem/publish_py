"""
Unit tests for domain.models.qid module.

Tests for QidRecord.
"""

import pytest
from src.db_models.shared_models import (
    QidRecord,
)


class TestQidRecord:
    """Tests for QidRecord dataclass."""

    def test_create_valid_qid_record(self):
        """Test creating a valid QidRecord."""
        record = QidRecord(
            id=1,
            title="TestArticle",
            qid="Q12345",
            add_date="2024-01-01 12:00:00",
        )

        assert record.id == 1
        assert record.title == "TestArticle"
        assert record.qid == "Q12345"
        assert record.add_date == "2024-01-01 12:00:00"

    def test_to_dict_returns_correct_dict(self):
        """Test that to_dict returns the correct dictionary representation."""
        record = QidRecord(
            id=1,
            title="TestArticle",
            qid="Q12345",
            add_date="2024-01-01 12:00:00",
        )

        result = record.to_dict()

        assert result == {
            "id": 1,
            "title": "TestArticle",
            "qid": "Q12345",
            "add_date": "2024-01-01 12:00:00",
        }

    def test_raises_error_when_title_is_empty(self):
        """Test that ValueError is raised when title is empty."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            QidRecord(
                id=1,
                title="",
                qid="Q12345",
                add_date="2024-01-01 12:00:00",
            )

    def test_raises_error_when_qid_is_empty(self):
        """Test that ValueError is raised when QID is empty."""
        with pytest.raises(ValueError, match="QID cannot be empty"):
            QidRecord(
                id=1,
                title="TestArticle",
                qid="",
                add_date="2024-01-01 12:00:00",
            )

    def test_raises_error_when_qid_does_not_start_with_q(self):
        """Test that ValueError is raised when QID doesn't start with Q."""
        with pytest.raises(ValueError, match="Invalid QID format"):
            QidRecord(
                id=1,
                title="TestArticle",
                qid="12345",
                add_date="2024-01-01 12:00:00",
            )

    def test_raises_error_when_qid_has_no_digits(self):
        """Test that ValueError is raised when QID has no digits after Q."""
        with pytest.raises(ValueError, match="Invalid QID format"):
            QidRecord(
                id=1,
                title="TestArticle",
                qid="QABC",
                add_date="2024-01-01 12:00:00",
            )

    def test_raises_error_when_qid_is_just_q(self):
        """Test that ValueError is raised when QID is just 'Q'."""
        with pytest.raises(ValueError, match="Invalid QID format"):
            QidRecord(
                id=1,
                title="TestArticle",
                qid="Q",
                add_date="2024-01-01 12:00:00",
            )

    def test_accepts_valid_qid_with_large_number(self):
        """Test that large QID numbers are accepted."""
        record = QidRecord(
            id=1,
            title="TestArticle",
            qid="Q123456789",
            add_date="2024-01-01 12:00:00",
        )

        assert record.qid == "Q123456789"

    def test_accepts_valid_qid_with_small_number(self):
        """Test that small QID numbers are accepted."""
        record = QidRecord(
            id=1,
            title="TestArticle",
            qid="Q1",
            add_date="2024-01-01 12:00:00",
        )

        assert record.qid == "Q1"
