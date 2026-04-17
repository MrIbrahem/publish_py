"""
SQLAlchemy-based service for managing coordinators.
"""

from __future__ import annotations

import functools
import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.sqlalchemy_db.engine import get_session
from ..models.coordinator import CoordinatorRecord, _CoordinatorRecord

logger = logging.getLogger(__name__)


def list_coordinators() -> List[CoordinatorRecord]:
    """Return all coordinator records."""
    with get_session() as session:
        orm_objs = session.query(_CoordinatorRecord).order_by(_CoordinatorRecord.id.asc()).all()
        return [CoordinatorRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


@functools.lru_cache(maxsize=1)
def active_coordinators() -> List[str]:
    """Return all active coordinator records."""
    with get_session() as session:
        orm_objs = (
            session.query(_CoordinatorRecord)
            .filter(_CoordinatorRecord.is_active == 1)
            .order_by(_CoordinatorRecord.id.asc())
            .all()
        )
        return [orm_obj.username for orm_obj in orm_objs]


def get_coordinator(coordinator_id: int) -> CoordinatorRecord | None:
    """Get a coordinator record by ID."""
    with get_session() as session:
        orm_obj = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.id == coordinator_id).first()
        if not orm_obj:
            logger.warning(f"Coordinator record with ID {coordinator_id} not found")
            return None
        return CoordinatorRecord(**orm_obj.to_dict())


def get_coordinator_by_user(username: str) -> CoordinatorRecord | None:
    """Get a coordinator record by username."""
    with get_session() as session:
        orm_obj = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.username == username).first()
        if not orm_obj:
            return None
        return CoordinatorRecord(**orm_obj.to_dict())


def add_coordinator(username: str, is_active: int = 1) -> CoordinatorRecord:
    """Add a new coordinator record."""
    username = username.strip()
    if not username:
        raise ValueError("User is required")

    with get_session() as session:
        orm_obj = _CoordinatorRecord(username=username, is_active=is_active)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Coordinator '{username}' already exists") from None

        # Refresh to get the ID and other defaults
        session.refresh(orm_obj)
        active_coordinators.cache_clear()
        return CoordinatorRecord(**orm_obj.to_dict())


def add_or_update_coordinator(username: str, is_active: int = 1) -> CoordinatorRecord:
    """Add or update a coordinator record."""
    username = username.strip()
    if not username:
        raise ValueError("User is required")

    with get_session() as session:
        orm_obj = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.username == username).first()
        if orm_obj:
            orm_obj.is_active = is_active
        else:
            orm_obj = _CoordinatorRecord(username=username, is_active=is_active)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        active_coordinators.cache_clear()
        return CoordinatorRecord(**orm_obj.to_dict())


def update_coordinator(coordinator_id: int, **kwargs) -> CoordinatorRecord:
    """Update a coordinator record."""
    with get_session() as session:
        orm_obj = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.id == coordinator_id).first()
        if not orm_obj:
            raise ValueError(f"Coordinator record with ID {coordinator_id} not found")

        if not kwargs:
            return CoordinatorRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        active_coordinators.cache_clear()
        return CoordinatorRecord(**orm_obj.to_dict())


def delete_coordinator(coordinator_id: int) -> CoordinatorRecord:
    """Delete a coordinator record by ID."""
    with get_session() as session:
        orm_obj = session.query(_CoordinatorRecord).filter(_CoordinatorRecord.id == coordinator_id).first()
        if not orm_obj:
            raise ValueError(f"Coordinator record with ID {coordinator_id} not found")

        record = CoordinatorRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        active_coordinators.cache_clear()
        return record


def is_coordinator(username: str) -> bool:
    """Check if a username is a coordinator."""
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
