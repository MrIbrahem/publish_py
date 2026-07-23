"""
SQLAlchemy-based service for managing qids_others table.
"""

from __future__ import annotations

import logging

from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased

from ....extensions import db
from ...models import QidOthersRecord

logger = logging.getLogger(__name__)


def add_or_update_qid(title: str, qid: str) -> QidOthersRecord:
    """Add or update a QID for a title."""
    orm_obj = db.session.query(QidOthersRecord).filter(QidOthersRecord.title == title).first()
    if orm_obj:
        orm_obj.qid = qid
    else:
        orm_obj = QidOthersRecord(title=title, qid=qid)

    orm_obj.validate()

    try:
        db.session.add(orm_obj)
        db.session.commit()
        db.session.refresh(orm_obj)
    except Exception:
        db.session.rollback()
        raise
    return orm_obj


def insert(title: str, qid: str) -> bool:
    """
    Insert a new row, or fill a missing qid for an existing title.
    """
    title = (title or "").strip()
    qid = (qid or "").strip()
    if not title or not qid:
        return False
    try:
        existing = db.session.query(QidOthersRecord).filter(QidOthersRecord.title == title).first()
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


def update_qid(qid_id: int, title: str, qid: str) -> QidOthersRecord:
    """Update an existing row by primary key."""
    title = (title or "").strip()
    qid = (qid or "").strip()

    if not qid_id or not title or not qid:
        raise ValueError("qid_id, title, and qid are required")

    orm_obj = db.session.get(QidOthersRecord, qid_id)
    if not orm_obj:
        raise ValueError(f"record with ID {qid_id} not found")

    orm_obj.title = title
    orm_obj.qid = qid

    orm_obj.validate()

    try:
        db.session.commit()
        db.session.refresh(orm_obj)
    except Exception:
        db.session.rollback()
        raise
    return orm_obj


def update_record(qid_id: int, title: str, qid: str) -> bool:
    """Update an existing row by primary key."""
    try:
        update_qid(qid_id, title, qid)
        return True
    except Exception:
        logger.exception("Failed to update qid id=%r", qid_id)
        return False


def get_record_by_title(title: str) -> QidOthersRecord | None:
    """Get the QID for a page title."""
    orm_obj = db.session.query(QidOthersRecord).filter(QidOthersRecord.title == title).first()
    if not orm_obj:
        logger.warning(f"QID for title {title} not found")
        return None
    return orm_obj


def list_records(dis: str = "all") -> list[QidOthersRecord]:
    """Return records, optionally filtered by ``dis``.

    - ``"all"``: every row.
    - ``"empty"``: rows where qid is NULL or empty string.
    - ``"duplicate"``: rows that share a title or qid with another row.
    """
    base = db.session.query(QidOthersRecord)
    if dis == "empty":
        rows = (
            base.filter(or_(QidOthersRecord.qid.is_(None), QidOthersRecord.qid == ""))
            .order_by(QidOthersRecord.id.asc())
            .all()
        )
        return rows
    if dis == "duplicate":
        other = aliased(QidOthersRecord)
        rows = (
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
        return rows
    # default: all
    return base.order_by(QidOthersRecord.id.asc()).all()


def get_by_qid(qid: str) -> QidOthersRecord | None:
    """Get the first record matching the given qid string."""
    if not qid:
        return None
    return db.session.query(QidOthersRecord).filter(QidOthersRecord.qid == qid).first()


def get_by_id(qid_id: int) -> QidOthersRecord | None:
    """Get a record by its primary key ID."""
    return db.session.get(QidOthersRecord, qid_id)


def get_by_title(title: str) -> QidOthersRecord | None:
    """Get the record matching the given title."""
    if not title:
        return None
    return db.session.query(QidOthersRecord).filter(QidOthersRecord.title == title).first()


def list_qid_records() -> list[QidOthersRecord]:
    """Return all QID records (legacy alias kept for compatibility)."""
    return db.session.query(QidOthersRecord).order_by(QidOthersRecord.id.asc()).all()


def get_title_to_qid() -> dict[str, str]:
    """Retrieve title to QID mapping from database."""
    qids = list_qid_records()
    return {record.title: record.qid or "" for record in qids}


ServiceRecord = QidOthersRecord


class QidOthersService:
    """Service class for managing QID records."""

    def add_or_update(self, title: str, qid: str) -> ServiceRecord:
        """Add or update a record for a given title."""
        return add_or_update_qid(title=title, qid=qid)

    def update(self, qid_id: int, title: str, qid: str) -> ServiceRecord:
        """Update an existing record by its ID."""
        return update_qid(qid_id=qid_id, title=title, qid=qid)

    def get_record_by_title(self, title: str) -> ServiceRecord | None:
        """Retrieve the record for a given page title."""
        return get_record_by_title(title=title)

    def list_records(self, dis: str = "all") -> list[ServiceRecord]:
        """List QID records with optional filtering (all, empty, duplicate)."""
        return list_records(dis=dis)

    def list_qid_records(self) -> list[ServiceRecord]:
        """Return all QID records."""
        return list_qid_records()

    def get_title_to_qid(self) -> dict[str, str]:
        """Retrieve a mapping dictionary of title to QID."""
        return get_title_to_qid()

    def get_by_qid(self, qid: str) -> ServiceRecord | None:
        """Get the first record matching the specified QID string."""
        return get_by_qid(qid=qid)

    def get_by_title(self, title: str) -> ServiceRecord | None:
        """Get the record matching the specified title."""
        return get_by_title(title=title)

    def get_by_id(self, qid_id: int) -> ServiceRecord | None:
        """Get a record by its primary key ID."""
        return get_by_id(qid_id=qid_id)

    def insert(self, title: str, qid: str) -> bool:
        """Insert a new record or update if the title already exists."""
        return insert(title=title, qid=qid)

    def update_record(self, qid_id: int, title: str, qid: str) -> bool:
        """Update an existing record and return success status as boolean."""
        return update_record(qid_id=qid_id, title=title, qid=qid)


__all__ = [
    "QidOthersService",
    "add_or_update_qid",
    "update_qid",
    "get_record_by_title",
    "list_records",
    "list_qid_records",
    "get_title_to_qid",
    "get_by_qid",
    "get_by_title",
    "insert",
    "update_record",
    "get_by_id",
]
