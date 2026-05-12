"""
Unit tests for domain.models.category module.

Tests for CategoryRecord.
"""

import pytest
from src.sqlalchemy_app.sqlalchemy_models import CategoryRecord


class TestCategoryRecord:
    """Tests for CategoryRecord dataclass."""

    def test_create_valid_category_record(self):
        """Test creating a valid CategoryRecord."""
        record = CategoryRecord(
            id=1,
            category="TestCategory",
            campaign="TestCampaign",
            display="Test Display",
            category2="TestCategory2",
            depth=2,
            is_default=1,
        )

        assert record.id == 1
        assert record.category == "TestCategory"
        assert record.campaign == "TestCampaign"
        assert record.display == "Test Display"
        assert record.category2 == "TestCategory2"
        assert record.depth == 2
        assert record.is_default == 1

    def test_to_dict_returns_correct_dict(self):
        """Test that to_dict returns the correct dictionary representation."""
        record = CategoryRecord(
            id=1,
            category="TestCategory",
            campaign="TestCampaign",
            display="Test Display",
            category2="TestCategory2",
            depth=2,
            is_default=1,
        )

        result = record.to_dict()

        assert result == {
            "id": 1,
            "category": "TestCategory",
            "campaign": "TestCampaign",
            "display": "Test Display",
            "category2": "TestCategory2",
            "depth": 2,
            "is_default": 1,
        }

    def test_raises_error_when_category_is_empty(self):
        """Test that ValueError is raised when category is empty."""
        with pytest.raises(ValueError, match="Category name cannot be empty"):
            CategoryRecord(
                id=1,
                category="",
                campaign="TestCampaign",
            )

    def test_raises_error_when_campaign_is_empty(self):
        """Test that ValueError is raised when campaign is empty."""
        with pytest.raises(ValueError, match="Campaign name cannot be empty"):
            CategoryRecord(
                id=1,
                category="TestCategory",
                campaign="",
            )

    def test_default_values(self):
        """Test that default values are applied correctly."""
        record = CategoryRecord(
            id=1,
            category="TestCategory",
            campaign="TestCampaign",
        )

        assert record.display == ""
        assert record.category2 == ""
        assert record.is_default == 0
        assert record.depth == 0

    def test_depth_conversion(self):
        """Test that depth is converted to int."""
        record = CategoryRecord(
            id=1,
            category="TestCategory",
            campaign="TestCampaign",
            depth="5",
        )

        assert record.depth == 5

    def test_is_default_conversion(self):
        """Test that is_default is converted to int."""
        record = CategoryRecord(
            id=1,
            category="TestCategory",
            campaign="TestCampaign",
            is_default="1",
        )

        assert record.is_default == 1
