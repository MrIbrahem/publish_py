"""

SQLAlchemy-based service for managing coordinators.

"""

from __future__ import annotations

import functools
import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...exceptions import DuplicateUserError, UserNotFoundError
from ...models import AdminUserRecord
from ..delete_service import delete_record_by_pk
from ..utils import db_guard_rollback

logger = logging.getLogger(__name__)

# ── SELECT ───────────────────────────────────────────────


@functools.lru_cache(maxsize=1)
def active_coordinators() -> List[str]:
    """Return usernames of all active coordinators (cached)."""
    records = (
        db.session.query(AdminUserRecord)
        # .filter(AdminUserRecord.is_active == 1)
        .filter_by(is_active=1)
        .order_by(AdminUserRecord.id)
        .all()
    )
    return [r.username for r in records]


def is_active_coordinator(username: str) -> bool:
    """Check whether a single username is an active coordinator."""
    try:
        record = (
            db.session.query(AdminUserRecord)
            .filter(AdminUserRecord.username == username, AdminUserRecord.is_active)
            .first()
        )
        return record is not None
    except Exception:
        logger.exception("Failed to check coordinator status")
    return False


def list_coordinators() -> List[AdminUserRecord]:
    """
    Return all coordinators from the database.

    Returns a list of records, or an empty list on failure.
    """
    return db.session.query(AdminUserRecord).all()


def get_coordinator_by_id(coordinator_id: int) -> AdminUserRecord | None:
    """
    Get a coordinator by ID.
    """
    # record = db.session.query(AdminUserRecord).filter(AdminUserRecord.id == coordinator_id).first()
    record = db.session.get(AdminUserRecord, coordinator_id)
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

    record = db.session.query(AdminUserRecord).filter(AdminUserRecord.username == username).first()
    if record:
        # This assumes a UNIQUE constraint on the username column
        raise DuplicateUserError(f"Coordinator '{username}' already exists") from None

    record = AdminUserRecord(username=username, is_active=True)
    db.session.add(record)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        if "a foreign key constraint fails" in str(exc):
            raise UserNotFoundError(f"User '{username}' does not exist") from exc
        raise
    db.session.refresh(record)
    active_coordinators.cache_clear()
    return record


@db_guard_rollback
def set_coordinator_active(coordinator_id: int, is_active: bool) -> AdminUserRecord | None:
    """Toggle coordinator activity."""
    # record = get_coordinator_by_id(coordinator_id)
    record = db.session.query(AdminUserRecord).filter(AdminUserRecord.id == coordinator_id).first()
    if not record:
        return None

    record.is_active = is_active
    db.session.commit()
    db.session.refresh(record)
    return record


def delete_coordinator(coordinator_id: int) -> bool:
    deleted = delete_record_by_pk(AdminUserRecord, coordinator_id)
    active_coordinators.cache_clear()
    return deleted


__all__ = [
    "list_coordinators",
    "active_coordinators",
    "get_coordinator_by_id",
    "add_coordinator",
    "is_active_coordinator",
    "set_coordinator_active",
]
