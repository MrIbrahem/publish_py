"""Database handler for categories table.

Mirrors: php_src/bots/sql/retrieveCampaignCategories()

This module retrieves campaign category mappings from the database.
"""

from __future__ import annotations

import logging
from typing import Any, List

from ....config import DbConfig
from ...core.db_driver import Database
from ..models import CategoryRecord

logger = logging.getLogger(__name__)


class CategoriesDB:
    """
    MySQL-backed handler for campaign categories.
    """

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> CategoryRecord:
        return CategoryRecord(**row)

    def fetch_by_id(self, category_id: int) -> CategoryRecord | None:
        """Get a category by ID."""
        rows = self.db.fetch_query_safe(
            "SELECT id, category, campaign, display, category2, depth, is_default FROM categories WHERE id = %s",
            (category_id,),
        )
        if not rows:
            logger.warning(f"Category with ID {category_id} not found")
            return None
        return self._row_to_record(rows[0])

    def list(self) -> List[CategoryRecord]:
        rows = self.db.fetch_query_safe(
            "SELECT id, category, campaign, display, category2, depth, is_default FROM categories ORDER BY id ASC"
        )
        return [self._row_to_record(row) for row in rows]

    def fetch_by_campaign(self, campaign: str) -> CategoryRecord | None:
        """
        Get the category for a specific campaign.
        """
        rows = self.db.fetch_query_safe(
            "SELECT id, category, campaign, display, category2, depth, is_default FROM categories WHERE campaign = %s",
            (campaign,),
        )
        if not rows:
            logger.warning(f"Campaign {campaign} not found")
            return None

        return self._row_to_record(rows[0])

    def fetch_by_category(self, category: str) -> CategoryRecord | None:
        """
        Get the category for a specific category name.
        """
        rows = self.db.fetch_query_safe(
            "SELECT id, category, campaign, display, category2, depth, is_default FROM categories WHERE category = %s",
            (category,),
        )
        if not rows:
            logger.warning(f"Category {category} not found")
            return None

        return self._row_to_record(rows[0])

    def delete(self, category_id: int) -> None:
        """Delete a category by ID."""
        record = self.fetch_by_id(category_id)
        if not record:
            raise ValueError(f"Category with ID {category_id} not found")

        self.db.execute_query_safe("DELETE FROM categories WHERE id = %s", (category_id,), self.db.commit)

    def add(
        self,
        category: str,
        campaign: str | None = "",
        display: str | None = "",
        category2: str | None = "",
        depth: int = 0,
    ) -> CategoryRecord | None:
        """Add a new category."""
        self.db.execute_query_safe(
            """
                INSERT INTO categories (category, campaign, display, category2, depth)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    campaign = VALUES(campaign),
                    display = VALUES(display),
                    category2 = VALUES(category2),
                    depth = VALUES(depth)
            """,
            (category, campaign, display, category2, depth),
        )
        return self.fetch_by_category(category)


__all__ = [
    "CategoriesDB",
]
