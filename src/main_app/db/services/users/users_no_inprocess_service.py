"""
SQLAlchemy-based service for managing users_no_inprocess.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import UsersNoInprocessRecord

logger = logging.getLogger(__name__)


def list_users_no_inprocess() -> List[UsersNoInprocessRecord]:
    """Return all users_no_inprocess records."""
    orm_objs = db.session.query(UsersNoInprocessRecord).order_by(UsersNoInprocessRecord.id.asc()).all()
    return orm_objs


def list_active_users_no_inprocess() -> List[UsersNoInprocessRecord]:
    """Return all is_active users_no_inprocess records."""
    orm_objs = (
        db.session.query(UsersNoInprocessRecord)
        .filter(UsersNoInprocessRecord.is_active == 1)
        .order_by(UsersNoInprocessRecord.id.asc())
        .all()
    )
    return orm_objs


def get_users_no_inprocess(record_id: int) -> UsersNoInprocessRecord | None:
    """Get a users_no_inprocess record by ID."""
    orm_obj = db.session.get(UsersNoInprocessRecord, record_id)
    if not orm_obj:
        logger.warning(f"UsersNoInprocess record with ID {record_id} not found")
        return None
    return orm_obj


def get_users_no_inprocess_by_user(user: str) -> UsersNoInprocessRecord | None:
    """Get a users_no_inprocess record by username."""
    orm_obj = db.session.query(UsersNoInprocessRecord).filter(UsersNoInprocessRecord.user == user).first()
    if not orm_obj:
        return None
    return orm_obj


def add_users_no_inprocess(user: str, is_active: int = 1) -> UsersNoInprocessRecord:
    """Add a new users_no_inprocess record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    orm_obj = UsersNoInprocessRecord(user=user, is_active=is_active)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"UsersNoInprocess '{user}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def add_or_update_users_no_inprocess(user: str, is_active: int = 1) -> UsersNoInprocessRecord:
    """Add or update a users_no_inprocess record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    orm_obj = db.session.query(UsersNoInprocessRecord).filter(UsersNoInprocessRecord.user == user).first()
    if orm_obj:
        orm_obj.is_active = is_active
    else:
        orm_obj = UsersNoInprocessRecord(user=user, is_active=is_active)
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_users_no_inprocess(record_id: int, **kwargs) -> UsersNoInprocessRecord:
    """Update a users_no_inprocess record."""
    orm_obj = db.session.get(UsersNoInprocessRecord, record_id)
    if not orm_obj:
        raise ValueError(f"UsersNoInprocess record with ID {record_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_users_no_inprocess(record_id: int) -> bool:
    """Delete a users_no_inprocess record by ID."""
    # orm_obj = db.session.query(UsersNoInprocessRecord).filter(UsersNoInprocessRecord.id == record_id).first()
    orm_obj = db.session.get(UsersNoInprocessRecord, record_id)
    if not orm_obj:
        raise ValueError(f"UsersNoInprocess record with ID {record_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(UsersNoInprocessRecord, record_id)
    return deleted is None


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
    "delete_users_no_inprocess",
    "should_hide_from_inprocess",
]
