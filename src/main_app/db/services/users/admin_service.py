"""
SQLAlchemy-based service for managing coordinators.
"""

from __future__ import annotations

import functools
import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import AdminUserRecord

logger = logging.getLogger(__name__)


def list_coordinators() -> List[AdminUserRecord]:
    """Return all coordinator records."""
    orm_objs = db.session.query(AdminUserRecord).order_by(AdminUserRecord.id).all()
    return orm_objs


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


def get_coordinator(coordinator_id: int) -> AdminUserRecord | None:
    """Get a coordinator record by ID."""
    # record = db.session.query(AdminUserRecord).filter(AdminUserRecord.id == coordinator_id).first()
    record = db.session.get(AdminUserRecord, coordinator_id)
    if not record:
        logger.warning(f"Coordinator record with ID {coordinator_id} not found")
        return None
    return record


def get_coordinator_by_user(username: str) -> AdminUserRecord | None:
    """Get a coordinator record by username."""
    # record = db.session.query(AdminUserRecord).filter(AdminUserRecord.username == username).first()
    record = db.session.query(AdminUserRecord).filter_by(username=username).first()
    if not record:
        return None
    return record


def add_coordinator(username: str, is_active: int = 1) -> AdminUserRecord:
    """Add a new coordinator. Raises ValueError if username already exists."""
    username = username.strip()
    if not username:
        raise ValueError("username is required")

    record = AdminUserRecord(username=username, is_active=is_active)
    db.session.add(record)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Coordinator '{username}' already exists") from None

    # Refresh to get the ID and other defaults
    db.session.refresh(record)
    active_coordinators.cache_clear()
    return record


def add_or_update_coordinator(username: str, is_active: int = 1) -> AdminUserRecord:
    """Add a coordinator or update is_active if already exists (UPSERT)."""
    username = username.strip()
    if not username:
        raise ValueError("username is required")

    record = db.session.query(AdminUserRecord).filter(AdminUserRecord.username == username).first()
    if record:
        record.is_active = is_active
    else:
        record = AdminUserRecord(username=username, is_active=is_active)
        db.session.add(record)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    db.session.refresh(record)
    active_coordinators.cache_clear()
    return record


def update_coordinator(coordinator_id: int, **kwargs) -> AdminUserRecord:
    """Update fields on a coordinator record. Raises ValueError if not found."""
    # record = db.session.query(AdminUserRecord).filter(AdminUserRecord.id == coordinator_id).first()
    record = db.session.get(AdminUserRecord, coordinator_id)
    if not record:
        raise ValueError(f"Coordinator with ID {coordinator_id} not found")

    if not kwargs:
        return record

    for key, value in kwargs.items():
        if hasattr(record, key):
            setattr(record, key, value)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    db.session.refresh(record)
    active_coordinators.cache_clear()

    return record


def delete_coordinator(coordinator_id: int) -> bool:
    """Delete a coordinator record by ID.

    Returns True when the record was deleted successfully, False otherwise.
    """
    # record = db.session.query(AdminUserRecord).filter(AdminUserRecord.id == coordinator_id).first()
    record = db.session.get(AdminUserRecord, coordinator_id)
    if not record:
        raise ValueError(f"Coordinator with ID {coordinator_id} not found")
    db.session.delete(record)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    active_coordinators.cache_clear()

    deleted = db.session.get(AdminUserRecord, coordinator_id)
    return deleted is None


def is_coordinator(username: str) -> bool:
    """Check if a username is an active coordinator."""
    record = get_coordinator_by_user(username)
    return record is not None and record.is_active == 1


def set_coordinator_active(coordinator_id: int, is_active: bool) -> AdminUserRecord:
    """Toggle coordinator activity and refresh settings."""
    return update_coordinator(coordinator_id, is_active=1 if is_active else 0)


__all__ = [
    "list_coordinators",
    "active_coordinators",
    "get_coordinator",
    "get_coordinator_by_user",
    "add_coordinator",
    "add_or_update_coordinator",
    "update_coordinator",
    "delete_coordinator",
    "is_coordinator",
    "set_coordinator_active",
]
