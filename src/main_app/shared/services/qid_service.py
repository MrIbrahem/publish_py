"""
SQLAlchemy-based service for managing QIDs.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import func

from ...sqlalchemy_models import QidRecord
from ..core.extensions import db

logger = logging.getLogger(__name__)


def add_qid(title: str, qid: str) -> QidRecord:
    """Add or update a QID for a title."""
    orm_obj = db.session.query(QidRecord).filter(QidRecord.title == title).first()
    if orm_obj:
        orm_obj.qid = qid
    else:
        orm_obj = QidRecord(title=title, qid=qid, add_date=func.now())
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_qid(qid_id: int, title: str, qid: str) -> QidRecord:
    """Update a QID record."""
    orm_obj = db.session.query(QidRecord).filter(QidRecord.id == qid_id).first()
    if not orm_obj:
        raise ValueError(f"QID record with ID {qid_id} not found")

    orm_obj.title = title
    orm_obj.qid = qid
    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_qid(qid_id: int) -> None:
    """Delete a QID record."""
    orm_obj = db.session.query(QidRecord).filter(QidRecord.id == qid_id).first()
    if not orm_obj:
        raise ValueError(f"QID record with ID {qid_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()


def get_page_qid(title: str) -> QidRecord | None:
    """Get the QID for a page title."""
    orm_obj = db.session.query(QidRecord).filter(QidRecord.title == title).first()
    if not orm_obj:
        logger.warning(f"QID for title {title} not found")
        return None
    return orm_obj


def list_qids() -> List[QidRecord]:
    """Return all QID records."""
    orm_objs = db.session.query(QidRecord).order_by(QidRecord.id.asc()).all()
    return orm_objs


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
