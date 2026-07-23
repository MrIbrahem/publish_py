"""
SQLAlchemy-based shared logic for managing QID-like tables.

This module centralizes the logic that is identical between
``qid_service.py`` and ``qid_others_service.py`` (and any future
table that follows the same ``title``/``qid`` structure).

Each table-specific service module should only need to:
1. Import its own ORM model.
2. Instantiate ``BaseQidService`` with that model.
3. Re-export module-level functions if backward-compatible
   free functions are needed (see ``qid_service.py`` for an example).
"""

from __future__ import annotations

import logging

from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased

from ..delete_service import delete_record_by_pk

from ....extensions import db
from ...models import QidRecord, QidOthersRecord

logger = logging.getLogger(__name__)

ServiceRecord = QidRecord | QidOthersRecord

def add_or_update_qid(model: type[ServiceRecord], title: str, qid: str) -> ServiceRecord:
    """Add or update a QID for a title."""
    orm_obj = db.session.query(model).filter(model.title == title).first()
    if orm_obj:
        orm_obj.qid = qid
    else:
        orm_obj = model(title=title, qid=qid)

    orm_obj.validate()

    try:
        db.session.add(orm_obj)
        db.session.commit()
        db.session.refresh(orm_obj)
    except Exception:
        db.session.rollback()
        raise
    return orm_obj


def insert(model: type[ServiceRecord], title: str, qid: str) -> bool:
    """
    Insert a new row, or fill a missing qid for an existing title.
    """
    title = (title or "").strip()
    qid = (qid or "").strip()
    if not title or not qid:
        return False

    # TODO: validate qid

    try:
        existing = db.session.query(model).filter(model.title == title).first()
        if existing:
            if not existing.qid:
                existing.qid = qid
                db.session.commit()
            return True

        orm_obj = model(title=title, qid=qid)
        db.session.add(orm_obj)
        db.session.commit()
        return True
    except Exception:
        logger.exception("Failed to insert record title=%r qid=%r", title, qid)
        db.session.rollback()
        return False


def update_qid(model: type[ServiceRecord], qid_id: int, title: str, qid: str) -> ServiceRecord:
    """Update an existing row by primary key."""
    title = (title or "").strip()
    qid = (qid or "").strip()

    if not qid_id or not title or not qid:
        raise ValueError("qid_id, title, and qid are required")

    orm_obj = db.session.get(model, qid_id)
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


def update_record(model: type[ServiceRecord], qid_id: int, title: str, qid: str) -> bool:
    """Update an existing row by primary key."""
    try:
        update_qid(model, qid_id, title, qid)
        return True
    except Exception:
        logger.exception("Failed to update qid id=%r", qid_id)
        return False


def get_record_by_title(model: type[ServiceRecord], title: str) -> None | ServiceRecord:
    """Get the QID for a page title."""
    orm_obj = db.session.query(model).filter(model.title == title).first()
    if not orm_obj:
        logger.warning(f"QID for title {title} not found")
        return None
    return orm_obj


def list_records(model: type[ServiceRecord], dis: str = "all") -> list:
    """Return records, optionally filtered by ``dis``.

    - ``"all"``: every row.
    - ``"empty"``: rows where qid is NULL or empty string.
    - ``"duplicate"``: rows that share a title or qid with another row.
    """
    base = db.session.query(model)
    if dis == "empty":
        rows = (
            base.filter(or_(model.qid.is_(None), model.qid == ""))
            .order_by(model.id.asc())
            .all()
        )
        return rows
    if dis == "duplicate":
        other = aliased(model)
        rows = (
            base.join(
                other,
                and_(
                    model.id != other.id,
                    or_(
                        model.qid == other.qid,
                        model.title == other.title,
                    ),
                ),
            )
            .order_by(model.id.asc())
            .distinct()
            .all()
        )
        return rows
    # default: all
    return base.order_by(model.id.asc()).all()


def get_by_qid(model: type[ServiceRecord], qid: str) -> None | ServiceRecord:
    """Get the first record matching the given qid string."""
    if not qid:
        return None
    return db.session.query(model).filter(model.qid == qid).first()


def get_by_id(model: type[ServiceRecord], qid_id: int) -> ServiceRecord | None:
    """Get a record by its primary key ID."""
    return db.session.get(model, qid_id)


def get_by_title(model: type[ServiceRecord], title: str) -> None | ServiceRecord:
    """Get the record matching the given title."""
    if not title:
        return None
    return db.session.query(model).filter(model.title == title).first()


def list_qid_records(model: type[ServiceRecord]) -> list[ServiceRecord]:
    """Return all QID records (legacy alias kept for compatibility)."""
    return db.session.query(model).order_by(model.id.asc()).all()


def get_title_to_qid(model: type[ServiceRecord]) -> dict[str, str]:
    """Retrieve title to QID mapping from database."""
    records = list_qid_records(model)
    return {record.title: record.qid or "" for record in records}


class BaseQidService:
    """Generic service class for managing QID-like records.

    Subclasses (or direct instances) are bound to a specific ORM
    model, e.g.::

        class QidService(BaseQidService):
            def __init__(self):
                super().__init__(QidRecord)
    """

    def __init__(self, model: type[ServiceRecord]) -> None:
        self.model = model

    def add_or_update(self, title: str, qid: str) -> ServiceRecord | None:
        """Add or update a record for a given title."""
        try:
            return add_or_update_qid(self.model, title=title, qid=qid)
        except Exception as e:
            logger.exception("Failed to add or update qid: %s", e)
            return None

    def update(self, qid_id: int, title: str, qid: str) -> ServiceRecord | None:
        """Update an existing record by its ID."""
        try:
            return update_qid(self.model, qid_id=qid_id, title=title, qid=qid)
        except Exception as e:
            logger.exception("Failed to update qid id=%r: %s", qid_id, e)
            return None

    def get_record_by_title(self, title: str) -> ServiceRecord | None:
        """Retrieve the record for a given page title."""
        try:
            return get_record_by_title(self.model, title=title)
        except Exception as e:
            logger.exception("Failed to get record by title: %s", e)
            return None

    def list_records(self, dis: str = "all") -> list[ServiceRecord]:
        """List QID records with optional filtering (all, empty, duplicate)."""
        try:
            return list_records(self.model, dis=dis)
        except Exception as e:
            logger.exception("Failed to list records: %s", e)
            return []

    def list_qid_records(self) -> list[ServiceRecord]:
        """Return all QID records."""
        try:
            return list_qid_records(self.model)
        except Exception as e:
            logger.exception("Failed to list qid records: %s", e)
            return []

    def get_title_to_qid(self) -> dict[str, str]:
        """Retrieve a mapping dictionary of title to QID."""
        try:
            return get_title_to_qid(self.model)
        except Exception as e:
            logger.exception("Failed to get title to qid: %s", e)
            return {}

    def get_by_qid(self, qid: str) -> ServiceRecord | None:
        """Get the first record matching the specified QID string."""
        try:
            return get_by_qid(self.model, qid=qid)
        except Exception as e:
            logger.exception("Failed to get record by qid: %s", e)
            return None

    def get_by_title(self, title: str) -> ServiceRecord | None:
        """Get the record matching the specified title."""
        try:
            return get_by_title(self.model, title=title)
        except Exception as e:
            logger.exception("Failed to get record by title: %s", e)
            return None

    def get_by_id(self, qid_id: int) -> ServiceRecord | None:
        """Get a record by its primary key ID."""
        try:
            return get_by_id(self.model, qid_id=qid_id)
        except Exception as e:
            logger.exception("Failed to get record by id: %s", e)

    def insert(self, title: str, qid: str) -> bool:
        """Insert a new record or update if the title already exists."""
        try:
            return insert(self.model, title=title, qid=qid)
        except Exception as e:
            logger.exception("Failed to insert qid: %s", e)
            return False

    def update_record(self, qid_id: int, title: str, qid: str) -> bool:
        """Update an existing record and return success status as boolean."""
        try:
            return update_record(self.model, qid_id=qid_id, title=title, qid=qid)
        except Exception as e:
            logger.exception("Failed to update qid id=%r: %s", qid_id, e)
            return False

    def delete(self, qid_id: int) -> bool:
        try:
            return delete_record_by_pk(self.model, qid_id)
        except Exception as e:
            logger.exception("Failed to delete qid id=%r: %s", qid_id, e)
            return False


__all__ = [
    "BaseQidService",
]
