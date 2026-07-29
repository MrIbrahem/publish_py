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
            return self.create(
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
    ) -> UserRecord:
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
        record = self.get_record_by_id(user_id)
        if record is None:
            raise ValueError(f"User record with ID {user_id} not found")

        try:
            return self.update(record, **data)
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

    def update_user_data(
        self,
        user_id: int,
        **kwargs,
    ) -> UserRecord | None:
        return self.update_by_id(user_id, kwargs)

    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        record = self.get_user_by_username(username)
        return record is not None

__all__ = [
    "UsersService",
]
