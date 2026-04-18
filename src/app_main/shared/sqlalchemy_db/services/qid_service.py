"""
SQLAlchemy-based service for managing QIDs.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ...domain.models import QidRecord
from ..engine import get_session
from ..models import _QidRecord

logger = logging.getLogger(__name__)


def add_qid(title: str, qid: str) -> QidRecord:
    """Add or update a QID for a title."""
    with get_session() as session:
        orm_obj = session.query(_QidRecord).filter(_QidRecord.title == title).first()
        if orm_obj:
            orm_obj.qid = qid
        else:
            orm_obj = _QidRecord(title=title, qid=qid, add_date=func.now())
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return QidRecord(**orm_obj.to_dict())


def update_qid(qid_id: int, title: str, qid: str) -> QidRecord:
    """Update a QID record."""
    with get_session() as session:
        orm_obj = session.query(_QidRecord).filter(_QidRecord.id == qid_id).first()
        if not orm_obj:
            raise ValueError(f"QID record with ID {qid_id} not found")

        orm_obj.title = title
        orm_obj.qid = qid
        session.commit()
        session.refresh(orm_obj)
        return QidRecord(**orm_obj.to_dict())


def delete_qid(qid_id: int) -> None:
    """Delete a QID record."""
    with get_session() as session:
        orm_obj = session.query(_QidRecord).filter(_QidRecord.id == qid_id).first()
        if not orm_obj:
            raise ValueError(f"QID record with ID {qid_id} not found")

        session.delete(orm_obj)
        session.commit()


def get_page_qid(title: str) -> QidRecord | None:
    """Get the QID for a page title."""
    with get_session() as session:
        orm_obj = session.query(_QidRecord).filter(_QidRecord.title == title).first()
        if not orm_obj:
            logger.warning(f"QID for title {title} not found")
            return None
        return QidRecord(**orm_obj.to_dict())


def list_qids() -> List[QidRecord]:
    """Return all QID records."""
    with get_session() as session:
        orm_objs = session.query(_QidRecord).order_by(_QidRecord.id.asc()).all()
        return [QidRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_title_to_qid() -> dict[str, str]:
    """Retrieve title to QID mapping from database."""
    qids = list_qids()
    return {record.title: record.qid or "" for record in qids}


__all__ = [
    "add_qid",
    "update_qid",
    "delete_qid",
    "get_page_qid",
    "list_qids",
    "get_title_to_qid",
]
