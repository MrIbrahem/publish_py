"""
SQLAlchemy-based service for managing users.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import UserRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class UsersService(CRUDService[UserRecord]):
    def __init__(self) -> None:
        super().__init__(db.session, UserRecord)

    def list_users(self) -> list[UserRecord]:
        """Return all user identity records."""
        return self.list_all()

    def get_user(self, user_id: int) -> UserRecord | None:
        """Fetch a user by user_id."""
        if not user_id:
            return None
        return self.get_record_by_id(user_id)

    def get_user_by_username(self, username: str) -> UserRecord | None:
        """Fetch a user by username."""
        username = (username or "").strip()
        if not username:
            return None
        return self.get_by(username=username)

    def create_user(self, username: str, **data) -> UserRecord:
        """Add a new user record."""
        username = username.strip()
        if not username:
            raise ValueError("Username is required")

        try:
            return user_crud.create(
                username=username,
                **data,
            )
        except IntegrityError:
            raise ValueError(f"User '{username}' already exists") from None

    def update_user(
        self,
        user_id: int,
        username: str,
        email: str = "",
        wiki: str = "",
        user_group: str = "Uncategorized",
    ) -> UserRecord | None:
        """Update a user record."""

        username = username.strip()
        if not username:
            raise ValueError("Username is required")
        data = {
            "username": username,
            "email": email,
            "wiki": wiki,
            "user_group": user_group,
        }
        try:
            return user_crud.update_by_id(
                user_id,
                data,
            )
        except ValueError as exc:
            raise ValueError(f"User record with ID {user_id} not found") from exc

    def users_search(self, userlike: str | None) -> list[str]:
        """Return all user records where there username start with userlike."""
        if not userlike:
            return []
        safe_prefix = userlike.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        rows = (
            self.session.query(UserRecord.username)
            .filter(UserRecord.username.like(f"{safe_prefix}%", escape="\\"))
            .order_by(UserRecord.username.asc())
            .limit(20)
            .all()
        )
        return [x.username for x in rows]

    def list_users_by_group(self, user_group: str) -> list[UserRecord]:
        """Return user records by group."""
        return list(
            self.list(
                filters={"user_group": user_group},
                order_by=[UserRecord.user_id.asc()],
            )
        )


user_crud = UsersService()


def list_users() -> list[UserRecord]:
    return user_crud.list_users()


def users_search(userlike: str | None) -> list[str]:
    return user_crud.users_search(userlike)


def list_users_by_group(user_group: str) -> list[UserRecord]:
    return user_crud.list_users_by_group(user_group)


def get_user(user_id: int) -> UserRecord | None:
    return user_crud.get_user(user_id)


def get_user_by_username(username: str) -> UserRecord | None:
    return user_crud.get_user_by_username(username)


def create_user(
    username: str,
    email: str = "",
    wiki: str = "",
    user_group: str = "Uncategorized",
) -> UserRecord:
    return user_crud.create_user(
        username,
        email=email,
        wiki=wiki,
        user_group=user_group,
    )


def update_user(
    user_id: int,
    username: str,
    email: str = "",
    wiki: str = "",
    user_group: str = "Uncategorized",
) -> UserRecord | None:
    return user_crud.update_user(user_id, username, email, wiki, user_group)


def update_user_data(
    user_id: int,
    **kwargs,
) -> UserRecord | None:
    return user_crud.update_by_id(user_id, kwargs)


def user_exists(username: str) -> bool:
    """Check if a user exists."""
    record = user_crud.get_user_by_username(username)
    return record is not None


__all__ = [
    "UsersService",
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
