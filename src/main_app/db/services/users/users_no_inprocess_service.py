"""
SQLAlchemy-based service for managing users_no_inprocess.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import UsersNoInprocessRecord
from ..base import CRUDService

logger = logging.getLogger(__name__)


class UsersNoInprocessService(CRUDService[UsersNoInprocessRecord, int]):
    model = UsersNoInprocessRecord


users_no_inprocess_crud = UsersNoInprocessService()


def list_users_no_inprocess() -> list[UsersNoInprocessRecord]:
    """Return all users_no_inprocess records."""
    return list(users_no_inprocess_crud.list(order_by=[UsersNoInprocessRecord.id.asc()]))


def list_active_users_no_inprocess() -> list[UsersNoInprocessRecord]:
    """Return all is_active users_no_inprocess records."""
    return list(users_no_inprocess_crud.list(filters={"is_active": 1}, order_by=[UsersNoInprocessRecord.id.asc()]))


def get_users_no_inprocess(record_id: int) -> UsersNoInprocessRecord | None:
    """Get a users_no_inprocess record by ID."""
    orm_obj = users_no_inprocess_crud.get(record_id)
    if not orm_obj:
        logger.warning(f"UsersNoInprocess record with ID {record_id} not found")
        return None
    return orm_obj


def get_users_no_inprocess_by_user(user: str) -> UsersNoInprocessRecord | None:
    """Get a users_no_inprocess record by username."""
    return users_no_inprocess_crud.get_by(user=user)


def add_users_no_inprocess(user: str, is_active: int = 1) -> UsersNoInprocessRecord:
    """Add a new users_no_inprocess record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    try:
        return users_no_inprocess_crud.create(user=user, is_active=is_active)
    except IntegrityError:
        raise ValueError(f"UsersNoInprocess '{user}' already exists") from None


def add_or_update_users_no_inprocess(user: str, is_active: int = 1) -> UsersNoInprocessRecord:
    """Add or update a users_no_inprocess record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    return users_no_inprocess_crud.upsert(keys={"user": user}, is_active=is_active)


def update_users_no_inprocess(record_id: int, **kwargs) -> UsersNoInprocessRecord:
    """Update a users_no_inprocess record."""
    if not kwargs:
        orm_obj = users_no_inprocess_crud.get(record_id)
        if not orm_obj:
            raise ValueError(f"UsersNoInprocess record with ID {record_id} not found")
        return orm_obj

    try:
        return users_no_inprocess_crud.update(record_id, **kwargs)
    except ValueError as exc:
        raise ValueError(f"UsersNoInprocess record with ID {record_id} not found") from exc


def should_hide_from_inprocess(user: str) -> bool:
    """Check if a user should be hidden from in-process list."""
    record = get_users_no_inprocess_by_user(user)
    return record is not None and record.is_active == 1


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
