"""
SQLAlchemy-based service for managing qids_others table.
"""

from __future__ import annotations

import logging
from typing import List

from ....shared.core.extensions import db
from ...models import QidOthersRecord

logger = logging.getLogger(__name__)


def add_qid_other(title: str, qid: str) -> QidOthersRecord:
    """Add or update a QID for a title."""
    orm_obj = db.session.query(QidOthersRecord).filter(QidOthersRecord.title == title).first()
    if orm_obj:
        orm_obj.qid = qid
    else:
        orm_obj = QidOthersRecord(title=title, qid=qid)
        db.session.add(orm_obj)

    try:
        db.session.commit()
        db.session.refresh(orm_obj)
    except Exception:
        db.session.rollback()
        raise
    return orm_obj


def update_qid_other(qid_id: int, title: str, qid: str) -> QidOthersRecord:
    """Update a QID record."""
    orm_obj = db.session.get(QidOthersRecord, qid_id)
    if not orm_obj:
        raise ValueError(f"QID record with ID {qid_id} not found")

    orm_obj.title = title
    orm_obj.qid = qid
    try:
        db.session.commit()
        db.session.refresh(orm_obj)
    except Exception:
        db.session.rollback()
        raise
    return orm_obj


def delete_qid_other(qid_id: int) -> bool:
    """Delete a QID record."""
    orm_obj = db.session.get(QidOthersRecord, qid_id)
    if not orm_obj:
        raise ValueError(f"QID record with ID {qid_id} not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = db.session.get(QidOthersRecord, qid_id)
    return deleted is None


def get_page_qid_other(title: str) -> QidOthersRecord | None:
    """Get the QID for a page title."""
    orm_obj = db.session.query(QidOthersRecord).filter(QidOthersRecord.title == title).first()
    if not orm_obj:
        logger.warning(f"QID for title {title} not found")
        return None
    return orm_obj


def list_qids_others() -> List[QidOthersRecord]:
    """Return all QID records."""
    orm_objs = db.session.query(QidOthersRecord).order_by(QidOthersRecord.id.asc()).all()
    return orm_objs


__all__ = [
    "add_qid_other",
    "update_qid_other",
    "delete_qid_other",
    "get_page_qid_other",
    "list_qids_others",
]
