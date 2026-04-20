"""
SQLAlchemy-based service for managing categories.
"""

from __future__ import annotations

import logging
from typing import List

from ...db_models.shared_models import CategoryRecord
from ..engine import get_session
from ..models import _CategoryRecord

logger = logging.getLogger(__name__)


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

    with get_session() as session:
        orm_obj = session.query(_CategoryRecord).filter(_CategoryRecord.category == category).first()
        if orm_obj:
            orm_obj.campaign = campaign
            orm_obj.display = display
            orm_obj.category2 = category2
            orm_obj.depth = depth
        else:
            orm_obj = _CategoryRecord(
                category=category,
                campaign=campaign,
                display=display,
                category2=category2,
                depth=depth,
            )
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        record = CategoryRecord(**orm_obj.to_dict())

        if is_default:
            # set this category as default by unsetting default flag on all other categories
            session.query(_CategoryRecord).update({_CategoryRecord.is_default: 0})
            orm_obj.is_default = 1
            session.commit()
            session.refresh(orm_obj)
            record = CategoryRecord(**orm_obj.to_dict())

        return record


def update_category(category_id: int, title: str, main_file: str) -> CategoryRecord:
    """Update category."""
    with get_session() as session:
        orm_obj = session.query(_CategoryRecord).filter(_CategoryRecord.id == category_id).first()
        if not orm_obj:
            raise ValueError(f"Category with ID {category_id} not found")

        orm_obj.category = title
        orm_obj.campaign = main_file

        session.commit()
        session.refresh(orm_obj)
        return CategoryRecord(**orm_obj.to_dict())


def delete_category(category_id: int) -> None:
    """Delete a category."""
    with get_session() as session:
        orm_obj = session.query(_CategoryRecord).filter(_CategoryRecord.id == category_id).first()
        if not orm_obj:
            raise ValueError(f"Category with ID {category_id} not found")

        session.delete(orm_obj)
        session.commit()


def get_campaign_category(campaign: str) -> CategoryRecord | None:
    """Get the category for a campaign."""
    with get_session() as session:
        orm_obj = session.query(_CategoryRecord).filter(_CategoryRecord.campaign == campaign).first()
        if not orm_obj:
            logger.warning(f"Campaign {campaign} not found")
            return None
        return CategoryRecord(**orm_obj.to_dict())


def list_categories() -> List[CategoryRecord]:
    """Return all categories."""
    with get_session() as session:
        orm_objs = session.query(_CategoryRecord).order_by(_CategoryRecord.id.asc()).all()
        return [CategoryRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_camp_to_cats() -> dict[str, str]:
    """Retrieve campaign to category mapping from database."""
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
