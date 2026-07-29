"""
SQLAlchemy-based service for managing translate types.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import UniqueError, db
from ...models import PageRecord, QidRecord, TranslateTypeRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class TranslateTypeService(CRUDService[TranslateTypeRecord]):
    model = TranslateTypeRecord

    def __init__(self):
        super().__init__(db.session, TranslateTypeRecord)

    def list_translate_types(self, cat: str = "All") -> list[TranslateTypeRecord]:
        """Return translate_type records, optionally filtered by category membership.

        When ``cat != "All"``, only records whose ``tt_title`` matches a page in the
        given category are returned.
        """
        query = self.session.query(TranslateTypeRecord)
        if cat and cat.lower() != "all":
            titles_in_cat = self.session.query(PageRecord.title).filter(PageRecord.cat == cat).distinct()
            query = query.filter(TranslateTypeRecord.tt_title.in_(titles_in_cat))
        return query.order_by(TranslateTypeRecord.tt_id.asc()).all()

    def list_new_titles(self) -> list[str]:
        """Return titles in the qids table that are not yet in translate_type."""
        existing_titles = self.session.query(TranslateTypeRecord.tt_title).subquery()
        rows = (
            self.session.query(QidRecord.title)
            .filter(QidRecord.title.notin_(self.session.query(existing_titles.c.tt_title)))
            .distinct()
            .order_by(QidRecord.title.asc())
            .all()
        )
        return [row[0] for row in rows if row[0]]

    def list_lead_enabled_types(self) -> list[TranslateTypeRecord]:
        """Return translate_type records with lead enabled."""
        return list(
            self.list(
                filters={"tt_lead": 1},
                order_by=[TranslateTypeRecord.tt_id.asc()],
            )
        )

    def list_full_enabled_types(self) -> list[TranslateTypeRecord]:
        """Return translate_type records with full enabled."""
        return list(
            self.list(
                filters={"tt_full": 1},
                order_by=[TranslateTypeRecord.tt_id.asc()],
            )
        )

    def get_translate_type(self, tt_id: int) -> TranslateTypeRecord | None:
        """Get a translate_type record by ID."""
        orm_obj = self.get(tt_id)
        if not orm_obj:
            logger.warning(f"TranslateType record with ID {tt_id} not found")
            return None
        return orm_obj

    def get_translate_type_by_title(self, title: str) -> TranslateTypeRecord | None:
        """Get a translate_type record by title."""
        return self.get_by(tt_title=title)

    def add_translate_type(
        self,
        tt_title: str,
        tt_lead: int = 1,
        tt_full: int = 0,
    ) -> TranslateTypeRecord:
        """Add a new translate_type record."""
        tt_title = tt_title.strip()
        if not tt_title:
            raise ValueError("Title is required")

        try:
            return self.create(tt_title=tt_title, tt_lead=tt_lead, tt_full=tt_full)
        except IntegrityError:
            raise UniqueError(title=tt_title) from None

    def update_translate_type(
        self,
        tt_id: int,
        tt_title: str | None = None,
        tt_lead: int | None = None,
        tt_full: int | None = None,
    ) -> TranslateTypeRecord | None:
        """Update a translate_type record."""
        kwargs = {}
        if tt_title:
            tt_title = tt_title.strip()
            kwargs["tt_title"] = tt_title

        if tt_lead is not None:
            kwargs["tt_lead"] = int(tt_lead)

        if tt_full is not None:
            kwargs["tt_full"] = int(tt_full)

        try:
            return self.update_by_id(tt_id, kwargs)
        except IntegrityError:
            raise UniqueError(title=tt_title) from None
        except ValueError as exc:
            raise ValueError(f"TranslateType record with ID {tt_id} not found") from exc

    def can_translate_lead(self, title: str) -> bool:
        """Check if a title can be translated as lead."""
        record = self.get_translate_type_by_title(title)
        return record.tt_lead == 1 if record else True

    def can_translate_full(self, title: str) -> bool:
        """Check if a title can be translated as full."""
        record = self.get_translate_type_by_title(title)
        return record.tt_full == 1 if record else False


__all__ = [
    "TranslateTypeService",
]
