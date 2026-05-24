"""
SQLAlchemy-based service for managing qids_others table.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import aliased

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


def list_records(dis: str = "all") -> List[QidOthersRecord]:
    """Return qids_others records, optionally filtered by ``dis``.

    - ``"all"``: every row.
    - ``"empty"``: rows where qid is NULL or empty string.
    - ``"duplicate"``: rows that share a title or qid with another row.
    """
    base = db.session.query(QidOthersRecord)
    if dis == "empty":
        return (
            base.filter(or_(QidOthersRecord.qid.is_(None), QidOthersRecord.qid == ""))
            .order_by(QidOthersRecord.id.asc())
            .all()
        )
    if dis == "duplicate":
        other = aliased(QidOthersRecord)
        return (
            base.join(
                other,
                and_(
                    QidOthersRecord.id != other.id,
                    or_(
                        QidOthersRecord.qid == other.qid,
                        QidOthersRecord.title == other.title,
                    ),
                ),
            )
            .order_by(QidOthersRecord.id.asc())
            .distinct()
            .all()
        )
    return base.order_by(QidOthersRecord.id.asc()).all()


def get_by_qid(qid: str) -> QidOthersRecord | None:
    """Get the first qids_others record matching the given qid string."""
    if not qid:
        return None
    return db.session.query(QidOthersRecord).filter(QidOthersRecord.qid == qid).first()


def get_by_title(title: str) -> QidOthersRecord | None:
    """Get the qids_others record matching the given title."""
    if not title:
        return None
    return db.session.query(QidOthersRecord).filter(QidOthersRecord.title == title).first()


def insert(title: str, qid: str) -> bool:
    """Insert a new qids_others row, or fill a missing qid for an existing title."""
    title = (title or "").strip()
    qid = (qid or "").strip()
    if not title or not qid:
        return False
    try:
        existing = (
            db.session.query(QidOthersRecord).filter(QidOthersRecord.title == title).first()
        )
        if existing:
            if not existing.qid:
                existing.qid = qid
                db.session.commit()
            return True
        orm_obj = QidOthersRecord(title=title, qid=qid)
        db.session.add(orm_obj)
        db.session.commit()
        return True
    except Exception:
        logger.exception("Failed to insert qids_others title=%r qid=%r", title, qid)
        db.session.rollback()
        return False


def update(qid_id: int, title: str, qid: str) -> bool:
    """Update an existing qids_others row by primary key."""
    title = (title or "").strip()
    qid = (qid or "").strip()
    if not qid_id or not title or not qid:
        return False
    try:
        orm_obj = db.session.get(QidOthersRecord, qid_id)
        if not orm_obj:
            return False
        orm_obj.title = title
        orm_obj.qid = qid
        db.session.commit()
        return True
    except Exception:
        logger.exception("Failed to update qids_others id=%r", qid_id)
        db.session.rollback()
        return False


__all__ = [
    "add_qid_other",
    "update_qid_other",
    "delete_qid_other",
    "get_page_qid_other",
    "list_records",
    "get_by_qid",
    "get_by_title",
    "insert",
    "update",
]
