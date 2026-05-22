"""
SQLAlchemy-based service for managing pages_users_to_main.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import PagesUsersToMainRecord

logger = logging.getLogger(__name__)


def list_pages_users_to_main() -> List[PagesUsersToMainRecord]:
    """Return all pages_users_to_main records."""
    orm_objs = db.session.query(PagesUsersToMainRecord).order_by(PagesUsersToMainRecord.id.asc()).all()
    return orm_objs


def get_pages_users_to_main(record_id: int) -> PagesUsersToMainRecord | None:
    """Get a pages_users_to_main record by ID."""
    orm_obj = db.session.get(PagesUsersToMainRecord, record_id)
    if not orm_obj:
        logger.warning(f"PagesUsersToMain record with ID {record_id} not found")
        return None
    return orm_obj


def add_pages_users_to_main(
    id: int | None = None,
    new_target: str = "",
    new_user: str = "",
    new_qid: str = "",
) -> PagesUsersToMainRecord:
    """Add a new pages_users_to_main record."""
    orm_obj = PagesUsersToMainRecord(id=id, new_target=new_target, new_user=new_user, new_qid=new_qid)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Failed to add pages_users_to_main record: {e}") from None

    db.session.refresh(orm_obj)
    return orm_obj


def update_pages_users_to_main(record_id: int, **kwargs) -> PagesUsersToMainRecord:
    """Update a pages_users_to_main record."""
    orm_obj = db.session.get(PagesUsersToMainRecord, record_id)
    if not orm_obj:
        raise ValueError(f"PagesUsersToMain record with ID {record_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    try:
        db.session.commit()
        db.session.refresh(orm_obj)
    except Exception:
        db.session.rollback()
        raise
    return orm_obj


def delete_pages_users_to_main(record_id: int) -> bool:
    """Delete a pages_users_to_main record by ID."""
    # orm_obj = db.session.query(PagesUsersToMainRecord).filter(PagesUsersToMainRecord.id == record_id).first()
    orm_obj = db.session.get(PagesUsersToMainRecord, record_id)
    if not orm_obj:
        raise ValueError(f"PagesUsersToMain record with ID {record_id} not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = db.session.get(PagesUsersToMainRecord, record_id)
    return deleted is None


__all__ = [
    "list_pages_users_to_main",
    "get_pages_users_to_main",
    "add_pages_users_to_main",
    "update_pages_users_to_main",
    "delete_pages_users_to_main",
]
