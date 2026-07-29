"""
SQLAlchemy-based service for managing views new.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import ViewsNewRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class ViewsNewService(CRUDService[ViewsNewRecord]):
    model = ViewsNewRecord

    def __init__(self):
        super().__init__(db.session, ViewsNewRecord)

    def list_views_new(self) -> list[ViewsNewRecord]:
        """Return all views_new records."""
        return list(
            self.list(
                order_by=[ViewsNewRecord.id.asc()],
            )
        )

    def list_views_by_target(self, target: str, lang: str | None = None) -> list[ViewsNewRecord]:
        """Return views_new records for a specific target."""
        filters = {"target": target}
        if lang:
            filters["lang"] = lang
        return list(
            self.list(
                filters=filters,
                order_by=[ViewsNewRecord.year.desc()],
            )
        )

    def list_views_by_lang(self, lang: str) -> list[ViewsNewRecord]:
        """Return views_new records for a specific language."""
        return list(
            self.list(
                filters={"lang": lang},
                order_by=[ViewsNewRecord.id.asc()],
            )
        )

    def get_views_new(self, view_id: int) -> ViewsNewRecord | None:
        """Get a views_new record by ID."""
        orm_obj = self.get(view_id)
        if not orm_obj:
            logger.warning(f"ViewsNew record with ID {view_id} not found")
            return None
        return orm_obj

    def get_views_by_target_lang_year(self, target: str, lang: str, year: int) -> ViewsNewRecord | None:
        """Get a views_new record by target, language, and year."""
        return self.get_by(target=target, lang=lang, year=year)

    def add_views_new(
        self,
        target: str,
        lang: str,
        year: int,
        views: int | None = 0,
    ) -> ViewsNewRecord:
        """Add a new views_new record."""
        target = target.strip()
        lang = lang.strip()

        if not target:
            raise ValueError("Target is required")
        if not lang:
            raise ValueError("Language is required")

        try:
            return self.create(target=target, lang=lang, year=year, views=views)
        except IntegrityError:
            raise ValueError(f"Views record for '{target}' in '{lang}' for year {year} already exists") from None

    def add_or_update_views_new(
        self,
        target: str,
        lang: str,
        year: int,
        views: int | None = 0,
    ) -> ViewsNewRecord:
        """Add or update a views_new record."""
        target = target.strip()
        lang = lang.strip()

        if not target:
            raise ValueError("Target is required")
        if not lang:
            raise ValueError("Language is required")

        instance, is_new = self.upsert_by(
            keys={"target": target, "lang": lang, "year": year},
            views=views,
        )
        return instance

    def update_views_new(self, view_id: int, **kwargs) -> ViewsNewRecord:
        """Update a views_new record."""
        return self.update_or_404(view_id, **kwargs)

    def get_total_views_for_target(
        self,
        target: str,
        lang: str | None = None,
    ) -> int:
        """Get total views across all years for a target."""
        records = self.list_views_by_target(target, lang)
        return sum(r.views or 0 for r in records)

__all__ = [
    "ViewsNewService",
]
