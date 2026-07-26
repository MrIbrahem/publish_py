"""

SQLAlchemy-based service for managing coordinators.

"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...exceptions import DuplicateUserError, UserNotFoundError
from ...models import AdminUserRecord
from ..base import CRUDService
from ..delete_service import delete_record_by_pk
from ..utils import db_guard_rollback

logger = logging.getLogger(__name__)


class AdminUserService(CRUDService[AdminUserRecord, int]):
    model = AdminUserRecord


admin_crud = AdminUserService(db.session)

# ── SELECT ───────────────────────────────────────────────


def active_coordinators() -> list[str]:
    """Return usernames of all active coordinators."""
    records = admin_crud.list(filters={"is_active": 1}, order_by=[AdminUserRecord.id])
    return [r.username for r in records]


def is_active_coordinator(username: str) -> bool:
    """Check whether a single username is an active coordinator."""
    try:
        record = admin_crud.get_by(username=username, is_active=True)
        return record is not None
    except Exception:
        logger.exception("Failed to check coordinator status")
    return False


def list_coordinators() -> list[AdminUserRecord]:
    """
    Return all coordinators from the database.

    Returns a list of records, or an empty list on failure.
    """
    return list(admin_crud.list())


def get_coordinator_by_id(coordinator_id: int) -> AdminUserRecord | None:
    """
    Get a coordinator by ID.
    """
    record = admin_crud.get(coordinator_id)
    if not record:
        logger.warning(f"Coordinator record with ID {coordinator_id} not found")
        return None
    return record


# ── INSERT, UPDATE, SET ──────────────────────────────────


def add_coordinator(username: str) -> AdminUserRecord:
    """Add a coordinator."""
    username = username.strip()
    if not username:
        raise ValueError("Username is required")

    record = admin_crud.get_by(username=username)
    if record:
        # This assumes a UNIQUE constraint on the username column
        raise DuplicateUserError(f"Coordinator '{username}' already exists") from None

    try:
        return admin_crud.create(username=username, is_active=True)
    except IntegrityError as exc:
        if "a foreign key constraint fails" in str(exc):
            raise UserNotFoundError(f"User '{username}' does not exist") from exc
        raise


@db_guard_rollback
def set_coordinator_active(coordinator_id: int, is_active: bool) -> AdminUserRecord | None:
    """Toggle coordinator activity."""
    try:
        return admin_crud.update(coordinator_id, is_active=is_active)
    except ValueError:
        return None


def delete_coordinator(coordinator_id: int) -> bool:
    deleted = delete_record_by_pk(AdminUserRecord, coordinator_id)
    return deleted


__all__ = [
    "list_coordinators",
    "active_coordinators",
    "get_coordinator_by_id",
    "add_coordinator",
    "is_active_coordinator",
    "set_coordinator_active",
]
