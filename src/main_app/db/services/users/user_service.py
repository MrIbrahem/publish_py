"""
SQLAlchemy-based service for managing users.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import UserRecord

logger = logging.getLogger(__name__)


def list_users() -> List[UserRecord]:
    """Return all user records."""
    orm_objs = db.session.query(UserRecord).order_by(UserRecord.user_id.asc()).all()
    return orm_objs


def users_search(userlike: str | None) -> List[str]:
    """Return all user records where there username start with userlike."""
    if not userlike:
        return []
    query = db.session.query(UserRecord).filter(UserRecord.username.like(f"{userlike}%"))
    orm_objs = query.all()
    return [x.username for x in orm_objs]


def list_users_by_group(user_group: str) -> List[UserRecord]:
    """Return user records by group."""
    orm_objs = (
        db.session.query(UserRecord)
        .filter(UserRecord.user_group == user_group)
        .order_by(UserRecord.user_id.asc())
        .all()
    )
    return orm_objs


def get_user(user_id: int) -> UserRecord | None:
    """
    Get a user record by ID.
    """
    # db\.session\.query\((\w+)\).filter\(\1\.(id|\w+_id) == (id|\w+_id)\)\.first\(\)
    # orm_obj = db.session.get(UserRecord, user_id)
    # user_id is the primary key for UserRecord
    orm_obj = db.session.get(UserRecord, user_id)
    if not orm_obj:
        logger.warning(f"User record with ID {user_id} not found")
        return None
    return orm_obj


def get_user_by_username(username: str) -> UserRecord | None:
    """Get a user record by username."""
    orm_obj = db.session.query(UserRecord).filter(UserRecord.username == username).first()
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

    orm_obj = UserRecord(
        username=username,
        email=email,
        wiki=wiki,
        user_group=user_group,
        reg_date=func.now(),
    )
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"User '{username}' already exists") from None

    db.session.refresh(orm_obj)
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

    orm_obj = db.session.get(UserRecord, user_id)
    if not orm_obj:
        raise ValueError(f"User record with ID {user_id} not found")

    orm_obj.username = username
    orm_obj.email = email
    orm_obj.wiki = wiki
    orm_obj.user_group = user_group

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_user_data(
    user_id: int,
    **kwargs,
) -> UserRecord:
    """Update a user record."""
    orm_obj = db.session.get(UserRecord, user_id)
    if not orm_obj:
        raise ValueError(f"User record with ID {user_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


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
    "update_user",
    "update_user_data",
    "user_exists",
    "users_search",
]
