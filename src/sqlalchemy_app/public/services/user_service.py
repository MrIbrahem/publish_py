"""
SQLAlchemy-based service for managing users.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ...shared.engine import get_session
from ...sqlalchemy_models import UserRecord

logger = logging.getLogger(__name__)


def list_users() -> List[UserRecord]:
    """Return all user records."""
    with get_session() as session:
        orm_objs = session.query(UserRecord).order_by(UserRecord.user_id.asc()).all()
        return orm_objs


def list_users_by_group(user_group: str) -> List[UserRecord]:
    """Return user records by group."""
    with get_session() as session:
        orm_objs = (
            session.query(UserRecord)
            .filter(UserRecord.user_group == user_group)
            .order_by(UserRecord.user_id.asc())
            .all()
        )
        return orm_objs


def get_user(user_id: int) -> UserRecord | None:
    """Get a user record by ID."""
    with get_session() as session:
        orm_obj = session.query(UserRecord).filter(UserRecord.user_id == user_id).first()
        if not orm_obj:
            logger.warning(f"User record with ID {user_id} not found")
            return None
        return orm_obj


def get_user_by_username(username: str) -> UserRecord | None:
    """Get a user record by username."""
    with get_session() as session:
        orm_obj = session.query(UserRecord).filter(UserRecord.username == username).first()
        if not orm_obj:
            return None
        return orm_obj


def add_user(
    username: str,
    email: str = "",
    wiki: str = "",
    user_group: str = "Uncategorized",
) -> UserRecord:
    """Add a new user record."""
    username = username.strip()
    if not username:
        raise ValueError("Username is required")

    with get_session() as session:
        orm_obj = UserRecord(
            username=username,
            email=email,
            wiki=wiki,
            user_group=user_group,
            reg_date=func.now(),
        )
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"User '{username}' already exists") from None

        session.refresh(orm_obj)
        return orm_obj


def update_user(
    user_id: int,
    username: str,
    email: str = "",
    wiki: str = "",
    user_group: str = "Uncategorized",
) -> UserRecord:
    """Update a user record."""

    username = username.strip()
    if not username:
        raise ValueError("Username is required")

    with get_session() as session:
        orm_obj = session.query(UserRecord).filter(UserRecord.user_id == user_id).first()
        if not orm_obj:
            raise ValueError(f"User record with ID {user_id} not found")

        orm_obj.username = username
        orm_obj.email = email
        orm_obj.wiki = wiki
        orm_obj.user_group = user_group

        session.commit()
        session.refresh(orm_obj)
        return orm_obj


def update_user_data(
    user_id: int,
    **kwargs,
) -> UserRecord:
    """Update a user record."""
    with get_session() as session:
        orm_obj = session.query(UserRecord).filter(UserRecord.user_id == user_id).first()
        if not orm_obj:
            raise ValueError(f"User record with ID {user_id} not found")

        if not kwargs:
            return orm_obj

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return orm_obj


def delete_user(user_id: int) -> UserRecord:
    """Delete a user record by ID."""
    with get_session() as session:
        orm_obj = session.query(UserRecord).filter(UserRecord.user_id == user_id).first()
        if not orm_obj:
            raise ValueError(f"User record with ID {user_id} not found")

        record = UserRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def user_exists(username: str) -> bool:
    """Check if a user exists."""
    record = get_user_by_username(username)
    return record is not None


__all__ = [
    "list_users",
    "list_users_by_group",
    "get_user",
    "get_user_by_username",
    "add_user",
    "update_user_data",
    "delete_user",
    "user_exists",
]
