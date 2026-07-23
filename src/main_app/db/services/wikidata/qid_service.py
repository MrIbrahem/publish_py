"""
SQLAlchemy-based service for managing QIDs.
"""

from __future__ import annotations

import logging

from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased

from ....extensions import db
from ...models import QidRecord

logger = logging.getLogger(__name__)


def add_qid(title: str, qid: str) -> QidRecord:
    """Add or update a QID for a title."""
    orm_obj = db.session.query(QidRecord).filter(QidRecord.title == title).first()
    if orm_obj:
        orm_obj.qid = qid
    else:
        orm_obj = QidRecord(title=title, qid=qid)

    orm_obj.validate()

    try:
        db.session.add(orm_obj)
        db.session.commit()
        db.session.refresh(orm_obj)
    except Exception:
        db.session.rollback()
        raise
    return orm_obj


def update_qid(qid_id: int, title: str, qid: str) -> QidRecord:
    """Update a QID record."""
    orm_obj = db.session.get(QidRecord, qid_id)
    if not orm_obj:
        raise ValueError(f"QID record with ID {qid_id} not found")

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


def get_page_qid(title: str) -> QidRecord | None:
    """Get the QID for a page title."""
    orm_obj = db.session.query(QidRecord).filter(QidRecord.title == title).first()
    if not orm_obj:
        logger.warning(f"QID for title {title} not found")
        return None
    return orm_obj


def list_records(dis: str = "all") -> list[QidRecord]:
    """Return QID records, optionally filtered by ``dis``.

    - ``"all"``: every row in qids.
    - ``"empty"``: rows where qid is NULL or empty string.
    - ``"duplicate"``: rows that share a title or qid with another row.
    """
    base = db.session.query(QidRecord)
    if dis == "empty":
        rows = base.filter(or_(QidRecord.qid.is_(None), QidRecord.qid == "")).order_by(QidRecord.id.asc()).all()
        return rows
    if dis == "duplicate":
        other = aliased(QidRecord)
        rows = (
            base.join(
                other,
                and_(
                    QidRecord.id != other.id,
                    or_(QidRecord.qid == other.qid, QidRecord.title == other.title),
                ),
            )
            .order_by(QidRecord.id.asc())
            .distinct()
            .all()
        )
        return rows
    # default: all
    return base.order_by(QidRecord.id.asc()).all()


def get_by_qid(qid: str) -> QidRecord | None:
    """Get the first QID record matching the given qid string."""
    if not qid:
        return None
    return db.session.query(QidRecord).filter(QidRecord.qid == qid).first()


def get_by_id(qid_id: int) -> QidRecord | None:
    """Get a QID record by its primary key ID."""
    return db.session.get(QidRecord, qid_id)


def get_by_title(title: str) -> QidRecord | None:
    """Get the QID record matching the given title."""
    if not title:
        return None
    return db.session.query(QidRecord).filter(QidRecord.title == title).first()


def insert(title: str, qid: str) -> bool:
    """Insert a new qids row, or update an existing matching title with the new qid.

    Mirrors the PHP "INSERT ... WHERE NOT EXISTS, then fill empty qid" semantic.
    Returns True on success, False otherwise.
    """
    title = (title or "").strip()
    qid = (qid or "").strip()
    if not title or not qid:
        return False
    try:
        existing = db.session.query(QidRecord).filter(QidRecord.title == title).first()
        if existing:
            if not existing.qid:
                existing.qid = qid
                db.session.commit()
            return True

        orm_obj = QidRecord(title=title, qid=qid)
        db.session.add(orm_obj)
        db.session.commit()
        return True
    except Exception:
        logger.exception("Failed to insert qid title=%r qid=%r", title, qid)
        db.session.rollback()
        return False


def update(qid_id: int, title: str, qid: str) -> bool:
    """Update an existing qids row by primary key."""
    title = (title or "").strip()
    qid = (qid or "").strip()

    if not qid_id or not title or not qid:
        return False

    orm_obj = None

    try:
        orm_obj = db.session.get(QidRecord, qid_id)
    except Exception:
        logger.exception("Failed to update qid id=%r", qid_id)
        return False

    if not orm_obj:
        return False

    orm_obj.title = title
    orm_obj.qid = qid

    try:
        orm_obj.validate()
    except Exception:
        logger.exception("Failed to validate")
        return False

    try:
        db.session.commit()
        return True
    except Exception:
        logger.exception("Failed to update qid id=%r", qid_id)
        db.session.rollback()
        return False


def list_qid_records() -> list[QidRecord]:
    """Return all QID records (legacy alias kept for compatibility)."""
    return db.session.query(QidRecord).order_by(QidRecord.id.asc()).all()


def get_title_to_qid() -> dict[str, str]:
    """Retrieve title to QID mapping from database."""
    qids = list_qid_records()
    return {record.title: record.qid or "" for record in qids}


class QidService:
    """Service class for managing QID records."""

    def add_qid(self, title: str, qid: str) -> QidRecord:
        """Add or update a QID record for a given title."""
        return add_qid(title=title, qid=qid)

    def update_qid(self, qid_id: int, title: str, qid: str) -> QidRecord:
        """Update an existing QID record by its ID."""
        return update_qid(qid_id=qid_id, title=title, qid=qid)

    def get_page_qid(self, title: str) -> QidRecord | None:
        """Retrieve the QID record for a given page title."""
        return get_page_qid(title=title)

    def list_records(self, dis: str = "all") -> list[QidRecord]:
        """List QID records with optional filtering (all, empty, duplicate)."""
        return list_records(dis=dis)

    def list_qid_records(self) -> list[QidRecord]:
        """Return all QID records."""
        return list_qid_records()

    def get_title_to_qid(self) -> dict[str, str]:
        """Retrieve a mapping dictionary of title to QID."""
        return get_title_to_qid()

    def get_by_qid(self, qid: str) -> QidRecord | None:
        """Get the first QID record matching the specified QID string."""
        return get_by_qid(qid=qid)

    def get_by_title(self, title: str) -> QidRecord | None:
        """Get the QID record matching the specified title."""
        return get_by_title(title=title)

    def get_by_id(self, qid_id: int) -> QidRecord | None:
        """Get a QID record by its primary key ID."""
        return get_by_id(qid_id=qid_id)

    def insert(self, title: str, qid: str) -> bool:
        """Insert a new QID record or update if the title already exists."""
        return insert(title=title, qid=qid)

    def update(self, qid_id: int, title: str, qid: str) -> bool:
        """Update an existing QID record and return success status as boolean."""
        return update(qid_id=qid_id, title=title, qid=qid)


__all__ = [
    "QidService",
    "add_qid",
    "update_qid",
    "get_page_qid",
    "list_records",
    "list_qid_records",
    "get_title_to_qid",
    "get_by_qid",
    "get_by_title",
    "insert",
    "update",
    "get_by_id",
]
