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


views_new_crud = ViewsNewService()


def list_views_new() -> list[ViewsNewRecord]:
    """Return all views_new records."""
    return list(
        views_new_crud.list(
            order_by=[ViewsNewRecord.id.asc()],
        )
    )


def list_views_by_target(target: str, lang: str | None = None) -> list[ViewsNewRecord]:
    """Return views_new records for a specific target."""
    filters = {"target": target}
    if lang:
        filters["lang"] = lang
    return list(
        views_new_crud.list(
            filters=filters,
            order_by=[ViewsNewRecord.year.desc()],
        )
    )


def list_views_by_lang(lang: str) -> list[ViewsNewRecord]:
    """Return views_new records for a specific language."""
    return list(
        views_new_crud.list(
            filters={"lang": lang},
            order_by=[ViewsNewRecord.id.asc()],
        )
    )


def get_views_new(view_id: int) -> ViewsNewRecord | None:
    """Get a views_new record by ID."""
    orm_obj = views_new_crud.get(view_id)
    if not orm_obj:
        logger.warning(f"ViewsNew record with ID {view_id} not found")
        return None
    return orm_obj


def get_views_by_target_lang_year(target: str, lang: str, year: int) -> ViewsNewRecord | None:
    """Get a views_new record by target, language, and year."""
    return views_new_crud.get_by(target=target, lang=lang, year=year)


def add_views_new(
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
        return views_new_crud.create(target=target, lang=lang, year=year, views=views)
    except IntegrityError:
        raise ValueError(f"Views record for '{target}' in '{lang}' for year {year} already exists") from None


def add_or_update_views_new(
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

    record = views_new_crud.get_by(target=target, lang=lang, year=year)
    if record:
        return views_new_crud.update(
            record,
            views=views,
        )
    else:
        return views_new_crud.create(
            target=target,
            lang=lang,
            year=year,
            views=views,
        )


def update_views_new(view_id: int, **kwargs) -> ViewsNewRecord | None:
    """Update a views_new record."""
    if not kwargs:
        orm_obj = views_new_crud.get(view_id)
        if not orm_obj:
            raise ValueError(f"ViewsNew record with ID {view_id} not found")
        return orm_obj

    try:
        return views_new_crud.update_by_id(view_id, **kwargs)
    except ValueError as exc:
        raise ValueError(f"ViewsNew record with ID {view_id} not found") from exc


def get_total_views_for_target(
    target: str,
    lang: str | None = None,
) -> int:
    """Get total views across all years for a target."""
    records = list_views_by_target(target, lang)
    return sum(r.views or 0 for r in records)


__all__ = [
    "list_views_new",
    "list_views_by_target",
    "list_views_by_lang",
    "get_views_new",
    "get_views_by_target_lang_year",
    "add_views_new",
    "add_or_update_views_new",
    "update_views_new",
    "get_total_views_for_target",
]
