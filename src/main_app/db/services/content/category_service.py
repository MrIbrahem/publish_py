"""
SQLAlchemy-based service for managing categories.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from ....extensions import db
from ...models import CategoryRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class CategoryService(CRUDService[CategoryRecord, int]):
    model = CategoryRecord


category_crud = CategoryService(db.session)


def set_default_category(session: Session | Any) -> None:
    session.query(CategoryRecord).update({CategoryRecord.is_default: 0})


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

    orm_obj = category_crud.get_by(category=category)
    if orm_obj:
        orm_obj = category_crud.update(
            orm_obj.id,
            campaign=campaign or "",
            display=display or "",
            category2=category2,
            depth=depth,
        )
    else:
        orm_obj = category_crud.create(
            category=category,
            campaign=campaign,
            display=display,
            category2=category2,
            depth=depth,
        )

    if is_default:
        # set this category as default by unsetting default flag on all other categories
        set_default_category(db.session)
        orm_obj = category_crud.update(orm_obj.id, is_default=1)
    else:
        orm_obj = category_crud.update(orm_obj.id, is_default=0)

    return orm_obj


def update_category(
    category_id: int,
    category: str,
    campaign: str,
    display: str | None = "",
    category2: str | None = "",
    depth: int | str = 0,
    is_default: int = 0,
) -> CategoryRecord:
    """Update category."""
    try:
        orm_obj = category_crud.update(
            category_id,
            category=category,
            campaign=campaign,
            display=display or "",
            category2=category2 or "",
            depth=int(depth),
        )
    except ValueError as exc:
        raise ValueError(f"Category with ID {category_id} not found") from exc

    if is_default:
        # set this category as default by unsetting default flag on all other categories
        set_default_category(db.session)
        orm_obj = category_crud.update(orm_obj.id, is_default=1)
    else:
        orm_obj = category_crud.update(orm_obj.id, is_default=0)

    return orm_obj


def get_campaign_category(campaign: str) -> CategoryRecord | None:
    """Get the category for a campaign."""
    orm_obj = category_crud.get_by(campaign=campaign)
    if not orm_obj:
        logger.warning(f"Campaign {campaign} not found")
        return None
    return orm_obj


def list_categories() -> list[CategoryRecord]:
    """Return all categories."""
    return list(
        category_crud.list(
            order_by=[CategoryRecord.id.asc()],
        )
    )


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
