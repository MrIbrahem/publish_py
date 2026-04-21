"""
SQLAlchemy-based service for managing pages_users_to_main.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...shared.engine import get_session
from ...sqlalchemy_models import PagesUsersToMainRecord

logger = logging.getLogger(__name__)


def list_pages_users_to_main() -> List[PagesUsersToMainRecord]:
    """Return all pages_users_to_main records."""
    with get_session() as session:
        orm_objs = session.query(PagesUsersToMainRecord).order_by(PagesUsersToMainRecord.id.asc()).all()
        return [PagesUsersToMainRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_pages_users_to_main(record_id: int) -> PagesUsersToMainRecord | None:
    """Get a pages_users_to_main record by ID."""
    with get_session() as session:
        orm_obj = session.query(PagesUsersToMainRecord).filter(PagesUsersToMainRecord.id == record_id).first()
        if not orm_obj:
            logger.warning(f"PagesUsersToMain record with ID {record_id} not found")
            return None
        return PagesUsersToMainRecord(**orm_obj.to_dict())


def add_pages_users_to_main(
    id: int | None = None,
    new_target: str = "",
    new_user: str = "",
    new_qid: str = "",
) -> PagesUsersToMainRecord:
    """Add a new pages_users_to_main record."""
    with get_session() as session:
        orm_obj = PagesUsersToMainRecord(id=id, new_target=new_target, new_user=new_user, new_qid=new_qid)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise ValueError(f"Failed to add pages_users_to_main record: {e}") from None

        session.refresh(orm_obj)
        return PagesUsersToMainRecord(**orm_obj.to_dict())


def update_pages_users_to_main(record_id: int, **kwargs) -> PagesUsersToMainRecord:
    """Update a pages_users_to_main record."""
    with get_session() as session:
        orm_obj = session.query(PagesUsersToMainRecord).filter(PagesUsersToMainRecord.id == record_id).first()
        if not orm_obj:
            raise ValueError(f"PagesUsersToMain record with ID {record_id} not found")

        if not kwargs:
            return PagesUsersToMainRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return PagesUsersToMainRecord(**orm_obj.to_dict())


def delete_pages_users_to_main(record_id: int) -> PagesUsersToMainRecord:
    """Delete a pages_users_to_main record by ID."""
    with get_session() as session:
        orm_obj = session.query(PagesUsersToMainRecord).filter(PagesUsersToMainRecord.id == record_id).first()
        if not orm_obj:
            raise ValueError(f"PagesUsersToMain record with ID {record_id} not found")

        record = PagesUsersToMainRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


__all__ = [
    "list_pages_users_to_main",
    "get_pages_users_to_main",
    "add_pages_users_to_main",
    "update_pages_users_to_main",
    "delete_pages_users_to_main",
]
