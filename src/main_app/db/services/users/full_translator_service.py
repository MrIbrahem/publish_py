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

    def list_full_translators(self) -> list[FullTranslatorRecord]:
        """Return all full translator records."""
        return list(
            self.list(
                order_by=[FullTranslatorRecord.id.asc()],
            )
        )


    def list_active_full_translators(self) -> list[FullTranslatorRecord]:
        """Return all is_active full translator records."""
        return list(
            self.list(
                filters={"is_active": 1},
                order_by=[FullTranslatorRecord.id.asc()],
            )
        )


    def get_full_translator(self, translator_id: int) -> FullTranslatorRecord | None:
        """Get a full translator record by ID."""
        orm_obj = self.get(translator_id)
        if not orm_obj:
            logger.warning(f"Full translator record with ID {translator_id} not found")
            return None
        return orm_obj


    def get_full_translator_by_user(self, user: str) -> FullTranslatorRecord | None:
        """Get a full translator record by username."""
        return self.get_by(user=user)


    def add_full_translator(self, user: str, is_active: int = 1) -> FullTranslatorRecord:
        """Add a new full translator record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        try:
            return self.create(user=user, is_active=is_active)
        except IntegrityError:
            raise ValueError(f"Full translator '{user}' already exists") from None


    def add_or_update_full_translator(self, user: str, is_active: int = 1) -> FullTranslatorRecord:
        """Add or update a full translator record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        instance, is_new = self.upsert_by(
            keys={"user": user},
            is_active=is_active,
        )
        return instance


    def update_full_translator(self, translator_id: int, **kwargs) -> FullTranslatorRecord | None:
        """Update a full translator record."""
        return self.update_or_404(translator_id, **kwargs)


    def is_full_translator(self, user: str) -> bool:
        """Check if a user is a full translator."""
        record = self.get_full_translator_by_user(user)
        return record is not None and record.is_active == 1



_crud = FullTranslatorService()

list_full_translators= _crud.list_full_translators
list_active_full_translators = _crud.list_active_full_translators
get_full_translator = _crud.get_full_translator
get_full_translator_by_user = _crud.get_full_translator_by_user
add_full_translator = _crud.add_full_translator
add_or_update_full_translator = _crud.add_or_update_full_translator
update_full_translator = _crud.update_full_translator
is_full_translator = _crud.is_full_translator

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
