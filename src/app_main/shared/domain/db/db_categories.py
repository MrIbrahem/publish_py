"""Database handler for categories table.

Mirrors: php_src/bots/sql/retrieveCampaignCategories()

This module retrieves campaign category mappings from the database.
"""

from __future__ import annotations

import logging
from typing import Any, List

from ..models import CategoryRecord

from ....config import DbConfig
from ...core.db_driver import Database

logger = logging.getLogger(__name__)


class CategoriesDB:
    """
    MySQL-backed handler for campaign categories.
    """

    def __init__(self, db_data: DbConfig):
        self.db = Database(db_data)

    def _row_to_record(self, row: dict[str, Any]) -> CategoryRecord:
        return CategoryRecord(**row)

    def list(self) -> List[CategoryRecord]:
        rows = self.db.fetch_query_safe(
            "SELECT id, category, campaign, display, category2, depth, is_default FROM categories ORDER BY id ASC"
        )
        return [self._row_to_record(row) for row in rows]

    def fetch_by_campaign(self, campaign: str) -> CategoryRecord | None:
        """Get the category for a specific campaign.

        Args:
            campaign: Campaign name

        Returns:
            CategoryRecord if found, None otherwise
        """
        rows = self.db.fetch_query_safe(
            "SELECT id, category, campaign, display, category2, depth, is_default FROM categories WHERE campaign = %s",
            (campaign,),
        )
        if not rows:
            logger.warning(f"Campaign {campaign} not found")
            return None

        return self._row_to_record(rows[0])

    def delete(self, category_id: int) -> None:
        """Delete a category by ID."""
        record = self.fetch_by_id(category_id)
        if not record:
            raise ValueError(f"Category with ID {category_id} not found")

        self.db.execute_query_safe(
            "DELETE FROM categories WHERE id = %s",
            (category_id,), self.db.commit
        )

    def add(
        self,
        category: str,
        display: str | None = "",
        campaign: str | None = "",
        category2: str | None = "",
        depth: int = 0,
    ) -> CategoryRecord:
        """Add a new category."""
        self.db.execute_query_safe(
            """
                INSERT INTO categories (category, display, campaign, category2, depth)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    campaign = VALUES(campaign),
                    display = VALUES(display),
                    category2 = VALUES(category2),
                    depth = VALUES(depth)
            """,
            (category, display, campaign, category2, depth),
        )
        new_id = self.db.get_last_insert_id()
        return self.fetch_by_id(new_id)


__all__ = [
    "CategoriesDB",
]
