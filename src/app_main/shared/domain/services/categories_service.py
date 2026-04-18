"""
Utilities for managing categories
"""

from __future__ import annotations

import logging
from typing import List

from ....config import has_db_config, settings
from ..db.db_categories import CategoriesDB
from ..models import CategoryRecord

logger = logging.getLogger(__name__)

_category_STORE: CategoriesDB | None = None


def get_categories_db() -> CategoriesDB:
    global _category_STORE

    if _category_STORE is None:
        if not has_db_config():
            raise RuntimeError("CategoriesDB requires database configuration; no fallback store is available.")

        try:
            _category_STORE = CategoriesDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL CategoriesDB")
            raise RuntimeError("Unable to initialize CategoriesDB") from exc

    return _category_STORE


def add_category(
    category: str,
    display: str | None = "",
    campaign: str | None = "",
    category2: str | None = "",
    depth: int = 0,
    is_default: int = 0,
) -> CategoryRecord:
    """Add a category."""

    # fallback display to campaign name if display name is not provided
    display = display or campaign

    store = get_categories_db()
    record = store.add(category, display, campaign, category2, depth)

    if is_default:
        # set this category as default by unsetting default flag on all other categories
        store.set_default(record.id)

    return record


def update_category(category_id: int, title: str, main_file: str) -> CategoryRecord:
    """Update category."""

    store = get_categories_db()
    record = store.update(category_id, title, main_file)

    return record


def delete_category(category_id: int) -> None:
    """Delete a category."""

    store = get_categories_db()
    store.delete(category_id)


def get_campaign_category(campaign: str) -> CategoryRecord | None:
    """Get the category for a campaign, with caching.

    Args:
        campaign: Campaign name

    Returns:
        CategoryRecord if found, None otherwise
    """
    store = get_categories_db()
    return store.fetch_by_campaign(campaign)


def list_categories() -> List[CategoryRecord]:
    """Return all categories."""

    store = get_categories_db()

    pages = store.list()
    return pages


def get_camp_to_cats() -> dict[str, str]:
    """Retrieve campaign to category mapping from database.

    Returns:
        Dictionary mapping campaign names to category names
    """

    categories = list_categories()

    camp_to_cats: dict[str, str] = {record.campaign: record.category or "" for record in categories if record.campaign}
    return camp_to_cats


__all__ = [
    "add_category",
    "update_category",
    "delete_category",
    "get_campaign_category",
    "list_categories",
    "get_camp_to_cats",
]
