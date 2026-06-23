"""
SQLAlchemy-based service for managing categories.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.orm import Session

from ....shared.core.extensions import db
from ...models import CategoryRecord

logger = logging.getLogger(__name__)


def set_default_category(session: Session) -> None:
    session.query(CategoryRecord).update({CategoryRecord.is_default: 0})
    # orm_obj.is_default = 1
    # session.commit()
    # session.refresh(orm_obj)


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

    orm_obj = db.session.query(CategoryRecord).filter(CategoryRecord.category == category).first()
    if orm_obj:
        orm_obj.campaign = campaign or ""
        orm_obj.display = display or ""
        orm_obj.category2 = category2
        orm_obj.depth = depth
    else:
        orm_obj = CategoryRecord(
            category=category,
            campaign=campaign,
            display=display,
            category2=category2,
            depth=depth,
        )
        db.session.add(orm_obj)

    if is_default:
        # set this category as default by unsetting default flag on all other categories
        set_default_category(db.session)
        orm_obj.is_default = 1
    else:
        orm_obj.is_default = 0

    db.session.commit()
    db.session.refresh(orm_obj)

    return orm_obj


def update_category(
    category_id: int,
    category: str,
    campaign: str,
    display: str | None = "",
    category2: str | None = "",
    depth: int = 0,
    is_default: int = 0,
) -> CategoryRecord:
    """Update category."""
    orm_obj = db.session.get(CategoryRecord, category_id)
    if not orm_obj:
        raise ValueError(f"Category with ID {category_id} not found")

    orm_obj.category = category
    orm_obj.campaign = campaign
    orm_obj.display = display or ""

    orm_obj.category2 = category2 or ""

    orm_obj.depth = depth

    if is_default:
        # set this category as default by unsetting default flag on all other categories
        set_default_category(db.session)
        orm_obj.is_default = 1
    else:
        orm_obj.is_default = 0

    db.session.commit()
    db.session.refresh(orm_obj)

    return orm_obj


def get_campaign_category(campaign: str) -> CategoryRecord | None:
    """Get the category for a campaign."""
    orm_obj = db.session.query(CategoryRecord).filter(CategoryRecord.campaign == campaign).first()
    if not orm_obj:
        logger.warning(f"Campaign {campaign} not found")
        return None
    return orm_obj


def list_categories() -> List[CategoryRecord]:
    """Return all categories."""
    orm_objs = db.session.query(CategoryRecord).order_by(CategoryRecord.id.asc()).all()
    return orm_objs


def get_camp_to_cats() -> dict[str, str]:
    """Retrieve campaign to category mapping from database."""
    categories = list_categories()
    camp_to_cats: dict[str, str] = {record.campaign: record.category or "" for record in categories if record.campaign}
    return camp_to_cats


__all__ = [
    "add_category",
    "update_category",
    "get_campaign_category",
    "list_categories",
    "get_camp_to_cats",
]
