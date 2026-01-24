"""Database handler for categories table.

Mirrors: php_src/bots/sql/retrieveCampaignCategories()

This module retrieves campaign category mappings from the database.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from .db_class import Database

logger = logging.getLogger(__name__)


class CategoriesDB:
    """MySQL-backed handler for campaign categories."""

    def __init__(self, db_data: dict[str, Any]):
        self.db = Database(db_data)

    def retrieve_campaign_categories(self) -> dict[str, str]:
        """Retrieve campaign to category mapping from database.

        Mirrors PHP function:
        ```php
        function retrieveCampaignCategories() {
            $camp_to_cats = [];
            foreach (fetch_query('select id, category, category2, campaign, depth, def from categories;') as $k => $tab) {
                $camp_to_cats[$tab['campaign']] = $tab['category'];
            };
            return $camp_to_cats;
        }
        ```

        Returns:
            Dictionary mapping campaign names to category names
        """
        camp_to_cats: dict[str, str] = {}

        try:
            rows = self.db.fetch_query_safe(
                "SELECT campaign, category FROM categories"
            )
            for row in rows:
                campaign = row.get("campaign")
                category = row.get("category")
                if campaign:
                    camp_to_cats[campaign] = category or ""
        except Exception as e:
            logger.error(f"Failed to retrieve campaign categories: {e}")

        return camp_to_cats

    def get_category_for_campaign(self, campaign: str) -> str:
        """Get the category for a specific campaign.

        Args:
            campaign: Campaign name

        Returns:
            Category name, or empty string if not found
        """
        categories = self.retrieve_campaign_categories()
        return categories.get(campaign, "")


# Cached function to avoid repeated database queries
@lru_cache(maxsize=1)
def _get_cached_campaign_categories(db_data_hash: str, db_data: tuple) -> dict[str, str]:
    """Get cached campaign categories.

    Args:
        db_data_hash: Hash of db_data for cache invalidation
        db_data: Database configuration as tuple (for hashability)

    Returns:
        Dictionary mapping campaign names to category names
    """
    # Convert tuple back to dict
    db_dict = dict(db_data)
    categories_db = CategoriesDB(db_dict)
    return categories_db.retrieve_campaign_categories()


def get_campaign_category(campaign: str, db_data: dict[str, Any]) -> str:
    """Get the category for a campaign, with caching.

    Args:
        campaign: Campaign name
        db_data: Database configuration dictionary

    Returns:
        Category name, or empty string if not found
    """
    # Create a hashable version of db_data for caching
    db_data_tuple = tuple(sorted(db_data.items()))
    db_data_hash = str(hash(db_data_tuple))

    categories = _get_cached_campaign_categories(db_data_hash, db_data_tuple)
    return categories.get(campaign, "")


def clear_categories_cache() -> None:
    """Clear the cached campaign categories.

    Call this if the categories table is updated.
    """
    _get_cached_campaign_categories.cache_clear()


__all__ = [
    "CategoriesDB",
    "get_campaign_category",
    "clear_categories_cache",
]
