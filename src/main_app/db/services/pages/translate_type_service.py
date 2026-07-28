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


translate_type_crud = TranslateTypeService()


def list_translate_types(cat: str = "All") -> list[TranslateTypeRecord]:
    """Return translate_type records, optionally filtered by category membership.

    When ``cat != "All"``, only records whose ``tt_title`` matches a page in the
    given category are returned.
    """
    query = translate_type_crud.session.query(TranslateTypeRecord)
    if cat and cat.lower() != "all":
        titles_in_cat = translate_type_crud.session.query(PageRecord.title).filter(PageRecord.cat == cat).distinct()
        query = query.filter(TranslateTypeRecord.tt_title.in_(titles_in_cat))
    return query.order_by(TranslateTypeRecord.tt_id.asc()).all()


def list_new_titles() -> list[str]:
    """Return titles in the qids table that are not yet in translate_type."""
    existing_titles = translate_type_crud.session.query(TranslateTypeRecord.tt_title).subquery()
    rows = (
        translate_type_crud.session.query(QidRecord.title)
        .filter(QidRecord.title.notin_(translate_type_crud.session.query(existing_titles.c.tt_title)))
        .distinct()
        .order_by(QidRecord.title.asc())
        .all()
    )
    return [row[0] for row in rows if row[0]]


def list_lead_enabled_types() -> list[TranslateTypeRecord]:
    """Return translate_type records with lead enabled."""
    return list(
        translate_type_crud.list(
            filters={"tt_lead": 1},
            order_by=[TranslateTypeRecord.tt_id.asc()],
        )
    )


def list_full_enabled_types() -> list[TranslateTypeRecord]:
    """Return translate_type records with full enabled."""
    return list(
        translate_type_crud.list(
            filters={"tt_full": 1},
            order_by=[TranslateTypeRecord.tt_id.asc()],
        )
    )


def get_translate_type(tt_id: int) -> TranslateTypeRecord | None:
    """Get a translate_type record by ID."""
    orm_obj = translate_type_crud.get(tt_id)
    if not orm_obj:
        logger.warning(f"TranslateType record with ID {tt_id} not found")
        return None
    return orm_obj


def get_translate_type_by_title(title: str) -> TranslateTypeRecord | None:
    """Get a translate_type record by title."""
    return translate_type_crud.get_by(tt_title=title)


def add_translate_type(
    tt_title: str,
    tt_lead: int = 1,
    tt_full: int = 0,
) -> TranslateTypeRecord:
    """Add a new translate_type record."""
    tt_title = tt_title.strip()
    if not tt_title:
        raise ValueError("Title is required")

    try:
        return translate_type_crud.create(tt_title=tt_title, tt_lead=tt_lead, tt_full=tt_full)
    except IntegrityError:
        raise UniqueError(title=tt_title) from None


def update_translate_type(
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
        return translate_type_crud.update_by_id(tt_id, kwargs)
    except IntegrityError:
        raise UniqueError(title=tt_title) from None
    except ValueError as exc:
        raise ValueError(f"TranslateType record with ID {tt_id} not found") from exc


def can_translate_lead(title: str) -> bool:
    """Check if a title can be translated as lead."""
    record = get_translate_type_by_title(title)
    return record.tt_lead == 1 if record else True


def can_translate_full(title: str) -> bool:
    """Check if a title can be translated as full."""
    record = get_translate_type_by_title(title)
    return record.tt_full == 1 if record else False


__all__ = [
    "list_translate_types",
    "list_new_titles",
    "list_lead_enabled_types",
    "list_full_enabled_types",
    "get_translate_type",
    "get_translate_type_by_title",
    "add_translate_type",
    "update_translate_type",
    "can_translate_lead",
    "can_translate_full",
]
