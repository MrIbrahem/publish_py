"""
SQLAlchemy-based service for managing coordinators.
"""

from __future__ import annotations

import functools
import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...db_models import CoordinatorRecord
from ...sqlalchemy_models import _CoordinatorRecord
from ...shared.engine import get_session

logger = logging.getLogger(__name__)


def list_coordinators() -> List[CoordinatorRecord]:
    """Return all coordinator records."""
    with get_session() as session:
        orm_objs = session.query(_CoordinatorRecord).order_by(_CoordinatorRecord.id).all()
        # return orm_objs
        return [CoordinatorRecord(**record.to_dict()) for record in orm_objs]


@functools.lru_cache(maxsize=1)
def active_coordinators() -> List[str]:
    """Return usernames of all active coordinators (cached)."""
    with get_session() as session:
        records = (
            session.query(_CoordinatorRecord)
            # .filter(_CoordinatorRecord.is_active == 1)
            .filter_by(is_active=1)
            .order_by(_CoordinatorRecord.id)
            .all()
        )
        return [r.username for r in records]


def get_coordinator(coordinator_id: int) -> CoordinatorRecord | None:
    """Get a coordinator record by ID."""
    with get_session() as session:
        # record = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.id == coordinator_id).first()
        record = session.get(_CoordinatorRecord, coordinator_id)
        if not record:
            logger.warning(f"Coordinator record with ID {coordinator_id} not found")
            return None
        # return record
        return CoordinatorRecord(**record.to_dict())


def get_coordinator_by_user(username: str) -> CoordinatorRecord | None:
    """Get a coordinator record by username."""
    with get_session() as session:
        # record = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.username == username).first()
        record = session.query(_CoordinatorRecord).filter_by(username=username).first()
        if not record:
            return None
        return CoordinatorRecord(**record.to_dict())


def add_coordinator(username: str, is_active: int = 1) -> CoordinatorRecord:
    """Add a new coordinator. Raises ValueError if username already exists."""
    username = username.strip()
    if not username:
        raise ValueError("username is required")

    with get_session() as session:
        record = _CoordinatorRecord(username=username, is_active=is_active)
        session.add(record)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Coordinator '{username}' already exists") from None

        # Refresh to get the ID and other defaults
        session.refresh(record)
        active_coordinators.cache_clear()
        # return record
        return CoordinatorRecord(**record.to_dict())


def add_or_update_coordinator(username: str, is_active: int = 1) -> CoordinatorRecord:
    """Add a coordinator or update is_active if already exists (UPSERT)."""
    username = username.strip()
    if not username:
        raise ValueError("username is required")

    with get_session() as session:
        record = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.username == username).first()
        if record:
            record.is_active = is_active
        else:
            record = _CoordinatorRecord(username=username, is_active=is_active)
            session.add(record)
        session.commit()
        session.refresh(record)
        active_coordinators.cache_clear()
        # return record
        return CoordinatorRecord(**record.to_dict())


def update_coordinator(coordinator_id: int, **kwargs) -> CoordinatorRecord:
    """Update fields on a coordinator record. Raises ValueError if not found."""
    with get_session() as session:
        # record = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.id == coordinator_id).first()
        record = session.get(_CoordinatorRecord, coordinator_id)
        if not record:
            raise ValueError(f"Coordinator with ID {coordinator_id} not found")

        if not kwargs:
            return CoordinatorRecord(**record.to_dict())

        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
        session.commit()
        session.refresh(record)
        active_coordinators.cache_clear()
        # return record
        return CoordinatorRecord(**record.to_dict())


def delete_coordinator(coordinator_id: int) -> None:
    """Delete a coordinator record by ID."""
    with get_session() as session:
        # record = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.id == coordinator_id).first()
        record = session.get(_CoordinatorRecord, coordinator_id)
        if not record:
            raise ValueError(f"Coordinator with ID {coordinator_id} not found")
        session.delete(record)
        session.commit()
        active_coordinators.cache_clear()


def is_coordinator(username: str) -> bool:
    """Check if a username is an active coordinator."""
    record = get_coordinator_by_user(username)
    return record is not None and record.is_active == 1


def set_coordinator_active(coordinator_id: int, is_active: bool) -> CoordinatorRecord:
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
