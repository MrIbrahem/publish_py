"""
SQLAlchemy-based service for managing categories.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from ....extensions import db
from ...exceptions import RecordNotFoundError
from ...models import CategoryRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


def set_default_category(session: Session | Any) -> None:
    session.query(CategoryRecord).update({CategoryRecord.is_default: 0})


class CategoryService(CRUDService[CategoryRecord]):
    model = CategoryRecord

    def __init__(self):
        super().__init__(db.session, CategoryRecord)

    def add_category(
        self,
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

        orm_obj, is_new = self.upsert_by(
            keys={"category": category},
            campaign=campaign,
            display=display,
            category2=category2,
            depth=depth,
        )

        if is_default:
            # set this category as default by unsetting default flag on all other categories
            set_default_category(self.session)
            orm_obj = self.update(orm_obj, is_default=1)
        else:
            orm_obj = self.update(orm_obj, is_default=0)

        return orm_obj

    def update_category(
        self,
        category_id: int,
        category: str,
        campaign: str,
        display: str | None = "",
        category2: str | None = "",
        depth: int | str = 0,
        is_default: int = 0,
    ) -> CategoryRecord:
        """Update category."""
        record = self.get_record_by_id(category_id)
        if not record:
            raise RecordNotFoundError(f"Category with ID {category_id} not found")

        try:
            record = self.update(
                record,
                category=category,
                campaign=campaign,
                display=display or "",
                category2=category2 or "",
                depth=int(depth),
            )
        except ValueError as exc:
            raise ValueError(f"Error updating category: {exc}") from exc

        if is_default:
            # set this category as default by unsetting default flag on all other categories
            set_default_category(self.session)
            self.update(record, is_default=1)
        else:
            self.update(record, is_default=0)

        return record

    def get_campaign_category(self, campaign: str) -> CategoryRecord | None:
        """Get the category for a campaign."""
        orm_obj = self.get_by(campaign=campaign)
        if not orm_obj:
            logger.warning(f"Campaign {campaign} not found")
            return None
        return orm_obj

    def list_categories(self) -> list[CategoryRecord]:
        """Return all categories."""
        return list(
            self.list(
                order_by=[CategoryRecord.id.asc()],
            )
        )

    def get_camp_to_cats(self) -> dict[str, str]:
        """Retrieve campaign to category mapping from database."""
        categories = self.list_categories()
        camp_to_cats: dict[str, str] = {
            record.campaign: record.category or "" for record in categories if record.campaign
        }
        return camp_to_cats

__all__ = [
    "CategoryService",
]
