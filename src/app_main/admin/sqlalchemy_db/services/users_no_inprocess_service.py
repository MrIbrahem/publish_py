"""
SQLAlchemy-based service for managing users_no_inprocess.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.sqlalchemy_db.engine import get_session
from ...domain.models.users_no_inprocess import UsersNoInprocessRecord
from ..models import _UsersNoInprocessRecord

logger = logging.getLogger(__name__)


def list_users_no_inprocess() -> List[UsersNoInprocessRecord]:
    """Return all users_no_inprocess records."""
    with get_session() as session:
        orm_objs = session.query(_UsersNoInprocessRecord).order_by(_UsersNoInprocessRecord.id.asc()).all()
        return [UsersNoInprocessRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def list_active_users_no_inprocess() -> List[UsersNoInprocessRecord]:
    """Return all active users_no_inprocess records."""
    with get_session() as session:
        orm_objs = (
            session.query(_UsersNoInprocessRecord)
            .filter(_UsersNoInprocessRecord.active == 1)
            .order_by(_UsersNoInprocessRecord.id.asc())
            .all()
        )
        return [UsersNoInprocessRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_users_no_inprocess(record_id: int) -> UsersNoInprocessRecord | None:
    """Get a users_no_inprocess record by ID."""
    with get_session() as session:
        orm_obj = session.query(_UsersNoInprocessRecord).filter(_UsersNoInprocessRecord.id == record_id).first()
        if not orm_obj:
            logger.warning(f"UsersNoInprocess record with ID {record_id} not found")
            return None
        return UsersNoInprocessRecord(**orm_obj.to_dict())


def get_users_no_inprocess_by_user(user: str) -> UsersNoInprocessRecord | None:
    """Get a users_no_inprocess record by username."""
    with get_session() as session:
        orm_obj = session.query(_UsersNoInprocessRecord).filter(_UsersNoInprocessRecord.user == user).first()
        if not orm_obj:
            return None
        return UsersNoInprocessRecord(**orm_obj.to_dict())


def add_users_no_inprocess(user: str, active: int = 1) -> UsersNoInprocessRecord:
    """Add a new users_no_inprocess record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    with get_session() as session:
        orm_obj = _UsersNoInprocessRecord(user=user, active=active)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"UsersNoInprocess '{user}' already exists") from None

        session.refresh(orm_obj)
        return UsersNoInprocessRecord(**orm_obj.to_dict())


def add_or_update_users_no_inprocess(user: str, active: int = 1) -> UsersNoInprocessRecord:
    """Add or update a users_no_inprocess record."""
    user = user.strip()
    if not user:
        raise ValueError("User is required")

    with get_session() as session:
        orm_obj = session.query(_UsersNoInprocessRecord).filter(_UsersNoInprocessRecord.user == user).first()
        if orm_obj:
            orm_obj.active = active
        else:
            orm_obj = _UsersNoInprocessRecord(user=user, active=active)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return UsersNoInprocessRecord(**orm_obj.to_dict())


def update_users_no_inprocess(record_id: int, **kwargs) -> UsersNoInprocessRecord:
    """Update a users_no_inprocess record."""
    with get_session() as session:
        orm_obj = session.query(_UsersNoInprocessRecord).filter(_UsersNoInprocessRecord.id == record_id).first()
        if not orm_obj:
            raise ValueError(f"UsersNoInprocess record with ID {record_id} not found")

        if not kwargs:
            return UsersNoInprocessRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return UsersNoInprocessRecord(**orm_obj.to_dict())


def delete_users_no_inprocess(record_id: int) -> UsersNoInprocessRecord:
    """Delete a users_no_inprocess record by ID."""
    with get_session() as session:
        orm_obj = session.query(_UsersNoInprocessRecord).filter(_UsersNoInprocessRecord.id == record_id).first()
        if not orm_obj:
            raise ValueError(f"UsersNoInprocess record with ID {record_id} not found")

        record = UsersNoInprocessRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def should_hide_from_inprocess(user: str) -> bool:
    """Check if a user should be hidden from in-process list."""
    record = get_users_no_inprocess_by_user(user)
    return record is not None and record.active == 1


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
