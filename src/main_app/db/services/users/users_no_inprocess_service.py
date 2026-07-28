"""
SQLAlchemy-based service for managing users_no_inprocess.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import UsersNoInprocessRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class UsersNoInprocessService(CRUDService[UsersNoInprocessRecord]):
    model = UsersNoInprocessRecord

    def __init__(self):
        super().__init__(db.session, UsersNoInprocessRecord)

    def list_users_no_inprocess(self) -> list[UsersNoInprocessRecord]:
        """Return all users_no_inprocess records."""
        return list(
            self.list(
                order_by=[UsersNoInprocessRecord.id.asc()],
            )
        )

    def list_active_users_no_inprocess(self) -> list[UsersNoInprocessRecord]:
        """Return all is_active users_no_inprocess records."""
        return list(
            self.list(
                filters={"is_active": 1},
                order_by=[UsersNoInprocessRecord.id.asc()],
            )
        )

    def get_users_no_inprocess(self, record_id: int) -> UsersNoInprocessRecord | None:
        """Get a users_no_inprocess record by ID."""
        orm_obj = self.get(record_id)
        if not orm_obj:
            logger.warning(f"UsersNoInprocess record with ID {record_id} not found")
            return None
        return orm_obj

    def get_users_no_inprocess_by_user(self, user: str) -> UsersNoInprocessRecord | None:
        """Get a users_no_inprocess record by username."""
        return self.get_by(user=user)

    def add_users_no_inprocess(self, user: str, is_active: int = 1) -> UsersNoInprocessRecord:
        """Add a new users_no_inprocess record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        try:
            return self.create(user=user, is_active=is_active)
        except IntegrityError:
            raise ValueError(f"UsersNoInprocess '{user}' already exists") from None

    def add_or_update_users_no_inprocess(self, user: str, is_active: int = 1) -> UsersNoInprocessRecord:
        """Add or update a users_no_inprocess record."""
        user = user.strip()
        if not user:
            raise ValueError("User is required")

        instance, is_new = self.upsert_by(
            keys={"user": user},
            is_active=is_active,
        )
        return instance

    def update_users_no_inprocess(self, record_id: int, **kwargs) -> UsersNoInprocessRecord | None:
        """Update a users_no_inprocess record."""
        return self.update_or_404(record_id, **kwargs)

    def should_hide_from_inprocess(self, user: str) -> bool:
        """Check if a user should be hidden from in-process list."""
        record = self.get_users_no_inprocess_by_user(user)
        return record is not None and record.is_active == 1


_crud = UsersNoInprocessService()

list_users_no_inprocess = _crud.list_users_no_inprocess
list_active_users_no_inprocess = _crud.list_active_users_no_inprocess
get_users_no_inprocess = _crud.get_users_no_inprocess
get_users_no_inprocess_by_user = _crud.get_users_no_inprocess_by_user
add_users_no_inprocess = _crud.add_users_no_inprocess
add_or_update_users_no_inprocess = _crud.add_or_update_users_no_inprocess
update_users_no_inprocess = _crud.update_users_no_inprocess
should_hide_from_inprocess = _crud.should_hide_from_inprocess

__all__ = [
    "list_users_no_inprocess",
    "list_active_users_no_inprocess",
    "get_users_no_inprocess",
    "get_users_no_inprocess_by_user",
    "add_users_no_inprocess",
    "add_or_update_users_no_inprocess",
    "update_users_no_inprocess",
    "should_hide_from_inprocess",
]
