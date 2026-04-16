"""
Unit tests for categories_service module.

TODO: Add more tests for categories_service functions.
"""

from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.domain.services.categories_service import (
    add_category,
    delete_category,
    get_campaign_category,
    list_categories,
    update_category,
)


class TestGetCampaignCategory:
    """Tests for get_campaign_category function."""

    def test_returns_category_record(self, monkeypatch):
        """Test that function returns a CategoryRecord."""
        mock_store = MagicMock()
        mock_category = MagicMock()
        mock_store.fetch_by_campaign.return_value = mock_category
        monkeypatch.setattr(
            "src.app_main.shared.domain.services.categories_service.get_categories_db", lambda: mock_store
        )

        result = get_campaign_category("TestCampaign")

        assert result is mock_category
        mock_store.fetch_by_campaign.assert_called_once_with("TestCampaign")
