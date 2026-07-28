"""
SQLAlchemy-based service for managing full translators.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import FullTranslatorRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class FullTranslatorService(CRUDService[FullTranslatorRecord]):
    model = FullTranslatorRecord

    def __init__(self):
        super().__init__(db.session, FullTranslatorRecord)


full_translator_crud = FullTranslatorService()


def list_full_translators() -> list[FullTranslatorRecord]:
    """Return all full translator records."""
    return list(
        full_translator_crud.list(
            order_by=[FullTranslatorRecord.id.asc()],
        )
    )


def list_active_full_translators() -> list[FullTranslatorRecord]:
    """Return all is_active full translator records."""
    return list(
        full_translator_crud.list(
            filters={"is_active": 1},
            order_by=[FullTranslatorRecord.id.asc()],
        )
    )


def get_full_translator(translator_id: int) -> FullTranslatorRecord | None:
    """Get a full translator record by ID."""
    orm_obj = full_translator_crud.get(translator_id)
    if not orm_obj:
        logger.warning(f"Full translator record with ID {translator_id} not found")
        return None
    return orm_obj


def get_full_translator_by_user(user: str) -> FullTranslatorRecord | None:
    """Get a full translator record by username."""
    return full_translator_crud.get_by(user=user)


def add_full_translator(user: str, is_active: int = 1) -> FullTranslatorRecord:
    """Add a new full translator record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    try:
        return full_translator_crud.create(user=user, is_active=is_active)
    except IntegrityError:
        raise ValueError(f"Full translator '{user}' already exists") from None


def add_or_update_full_translator(user: str, is_active: int = 1) -> FullTranslatorRecord:
    """Add or update a full translator record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    record = full_translator_crud.get_by(user=user)
    if record:
        return full_translator_crud.update(record, is_active=is_active)
    else:
        return full_translator_crud.create(user=user, is_active=is_active)

def update_full_translator(translator_id: int, **kwargs) -> FullTranslatorRecord | None:
    """Update a full translator record."""
    if not kwargs:
        orm_obj = full_translator_crud.get(translator_id)
        if not orm_obj:
            raise ValueError(f"Full translator record with ID {translator_id} not found")
        return orm_obj

    try:
        return full_translator_crud.update_by_id(translator_id, **kwargs)
    except ValueError as exc:
        raise ValueError(f"Full translator record with ID {translator_id} not found") from exc


def is_full_translator(user: str) -> bool:
    """Check if a user is a full translator."""
    record = get_full_translator_by_user(user)
    return record is not None and record.is_active == 1


__all__ = [
    "list_full_translators",
    "list_active_full_translators",
    "get_full_translator",
    "get_full_translator_by_user",
    "add_full_translator",
    "add_or_update_full_translator",
    "update_full_translator",
    "is_full_translator",
]
