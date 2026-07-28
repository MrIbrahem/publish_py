"""
SQLAlchemy-based service for managing languages.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import LangRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class LangService(CRUDService[LangRecord]):
    model = LangRecord

    def __init__(self):
        super().__init__(db.session, LangRecord)


lang_crud = LangService()


def list_langs() -> list[LangRecord]:
    """Return all language records."""
    return list(
        lang_crud.list(
            order_by=[LangRecord.lang_id.asc()],
        )
    )


def get_lang(lang_id: int) -> LangRecord | None:
    """Get a language record by ID."""
    orm_obj = lang_crud.get(lang_id)
    if not orm_obj:
        logger.warning(f"Language record with ID {lang_id} not found")
        return None
    return orm_obj


def get_lang_by_code(code: str) -> LangRecord | None:
    """Get a language record by code."""
    return lang_crud.get_by(code=code)


def add_lang(
    code: str,
    autonym: str,
    name: str,
    redirects: list[str] | None = None,
) -> LangRecord:
    """Add a new language record."""
    code = code.strip()
    if not code:
        raise ValueError("Language code is required")

    try:
        return lang_crud.create(code=code, autonym=autonym, name=name, redirects=redirects)
    except IntegrityError:
        raise ValueError(f"Language '{code}' already exists") from None


def add_or_update_lang(
    code: str,
    autonym: str,
    name: str,
    redirects: list[str] | None = None,
) -> LangRecord:
    """Add or update a language record."""
    code = code.strip()
    if not code:
        raise ValueError("Language code is required")

    return lang_crud.upsert(keys={"code": code}, autonym=autonym, name=name, redirects=redirects)


__all__ = [
    "list_langs",
    "get_lang",
    "get_lang_by_code",
    "add_lang",
    "add_or_update_lang",
]
