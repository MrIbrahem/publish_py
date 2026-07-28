"""
SQLAlchemy-based service for managing enwiki pageviews.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import EnwikiPageviewRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class EnwikiPageviewService(CRUDService[EnwikiPageviewRecord]):
    model = EnwikiPageviewRecord

    def __init__(self):
        super().__init__(db.session, EnwikiPageviewRecord)

    def list_enwiki_pageviews(self) -> list[EnwikiPageviewRecord]:
        """Return all enwiki pageview records."""
        return list(
            self.list(
                order_by=[EnwikiPageviewRecord.id.asc()],
            )
        )


    def get_top_enwiki_pageviews(self,limit: int = 100) -> list[EnwikiPageviewRecord]:
        """Return top enwiki pageview records by view count."""
        return list(self.list(order_by=[EnwikiPageviewRecord.en_views.desc()], limit=limit))


    def get_enwiki_pageview(self,pageview_id: int) -> EnwikiPageviewRecord | None:
        """Get an enwiki pageview record by ID."""
        orm_obj = self.get(pageview_id)
        if not orm_obj:
            logger.warning(f"Enwiki pageview record with ID {pageview_id} not found")
            return None
        return orm_obj


    def get_enwiki_pageview_by_title(self,title: str) -> EnwikiPageviewRecord | None:
        """Get an enwiki pageview record by title."""
        return self.get_by(title=title)


    def add_enwiki_pageview(self,title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
        """Add a new enwiki pageview record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        try:
            return self.create(title=title, en_views=en_views)
        except IntegrityError:
            raise ValueError(f"Enwiki pageview for '{title}' already exists") from None


    def add_or_update_enwiki_pageview(self,title: str, en_views: int | None = 0) -> EnwikiPageviewRecord:
        """Add or update an enwiki pageview record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        instance, is_new = self.upsert_by(
            keys={"title": title},
            en_views=en_views,
        )
        return instance


    def update_enwiki_pageview(self,pageview_id: int, **kwargs) -> EnwikiPageviewRecord | None:
        """Update an enwiki pageview record."""
        return self.update_or_404(pageview_id, **kwargs)



enwiki_pageview_crud = EnwikiPageviewService()

list_enwiki_pageviews = enwiki_pageview_crud.list_enwiki_pageviews
get_top_enwiki_pageviews = enwiki_pageview_crud.get_top_enwiki_pageviews
get_enwiki_pageview = enwiki_pageview_crud.get_enwiki_pageview
get_enwiki_pageview_by_title = enwiki_pageview_crud.get_enwiki_pageview_by_title
add_enwiki_pageview = enwiki_pageview_crud.add_enwiki_pageview
add_or_update_enwiki_pageview = enwiki_pageview_crud.add_or_update_enwiki_pageview
update_enwiki_pageview = enwiki_pageview_crud.update_enwiki_pageview


__all__ = [
    "list_enwiki_pageviews",
    "get_top_enwiki_pageviews",
    "get_enwiki_pageview",
    "get_enwiki_pageview_by_title",
    "add_enwiki_pageview",
    "add_or_update_enwiki_pageview",
    "update_enwiki_pageview",
]
