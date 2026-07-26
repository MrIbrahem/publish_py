"""
SQLAlchemy-based service for managing users.
"""

from __future__ import annotations

import logging

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import UserRecord
from ..base import CRUDService

logger = logging.getLogger(__name__)


class UserService(CRUDService[UserRecord, int]):
    model = UserRecord


user_crud = UserService(db.session)


def list_users() -> list[UserRecord]:
    """Return all user records."""
    return list(user_crud.list(order_by=[UserRecord.user_id.asc()]))


def users_search(userlike: str | None) -> list[str]:
    """Return all user records where there username start with userlike."""
    if not userlike:
        return []
    safe_prefix = userlike.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows = (
        db.session.query(UserRecord.username)
        .filter(UserRecord.username.like(f"{safe_prefix}%", escape="\\"))
        .order_by(UserRecord.username.asc())
        .limit(20)
        .all()
    )
    return [x.username for x in rows]


def list_users_by_group(user_group: str) -> list[UserRecord]:
    """Return user records by group."""
    return list(user_crud.list(filters={"user_group": user_group}, order_by=[UserRecord.user_id.asc()]))


def get_user(user_id: int) -> UserRecord | None:
    """
    Get a user record by ID.
    """
    orm_obj = user_crud.get(user_id)
    if not orm_obj:
        logger.warning(f"User record with ID {user_id} not found")
        return None
    return orm_obj


def get_user_by_username(username: str) -> UserRecord | None:
    """Get a user record by username."""
    return user_crud.get_by(username=username)


def create_user(
    username: str,
    email: str = "",
    wiki: str = "",
    user_group: str = "Uncategorized",
) -> UserRecord:
    """Add a new user record."""
    username = username.strip()
    if not username:
        raise ValueError("Username is required")

    try:
        return user_crud.create(
            username=username,
            email=email,
            wiki=wiki,
            user_group=user_group,
            created_at=func.now(),
        )
    except IntegrityError:
        raise ValueError(f"User '{username}' already exists") from None


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

    try:
        return user_crud.update(
            user_id,
            username=username,
            email=email,
            wiki=wiki,
            user_group=user_group,
        )
    except ValueError as exc:
        raise ValueError(f"User record with ID {user_id} not found") from exc


def update_user_data(
    user_id: int,
    **kwargs,
) -> UserRecord:
    """Update a user record."""
    if not kwargs:
        orm_obj = user_crud.get(user_id)
        if not orm_obj:
            raise ValueError(f"User record with ID {user_id} not found")
        return orm_obj

    try:
        return user_crud.update(user_id, **kwargs)
    except ValueError as exc:
        raise ValueError(f"User record with ID {user_id} not found") from exc


def user_exists(username: str) -> bool:
    """Check if a user exists."""
    record = get_user_by_username(username)
    return record is not None


__all__ = [
    "list_users",
    "list_users_by_group",
    "get_user",
    "get_user_by_username",
    "create_user",
    "update_user",
    "update_user_data",
    "user_exists",
    "users_search",
]
