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
from typing import Any

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, aliased

from ....extensions import db
from ...models import QidOthersRecord, QidRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)

ServiceRecord = QidRecord | QidOthersRecord


def validate_or_raise(title: str, qid: str) -> None:
    # Validate that required fields are not empty
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    if not qid or not qid.strip():
        raise ValueError("QID cannot be empty")

    # Validate QID format (should start with Q followed by digits)
    if not qid.startswith("Q") or not qid[1:].isdigit():
        raise ValueError(f"Invalid QID format: {qid}. QID should start with 'Q' followed by digits.")


class BaseQidService(CRUDService[ServiceRecord]):
    """Generic service class for managing QID-like records.

    Subclasses (or direct instances) are bound to a specific ORM
    model, e.g.::

        class QidService(BaseQidService):
            def __init__(self):
                super().__init__(QidRecord, db.session)
    """

    def __init__(self, model: type[ServiceRecord], session: Session | Any) -> None:
        super().__init__(session, model)
        self.model = model

    # ───────────────────────────────────────────────────────────────
    # lists

    def list_records(self, dis: str = "all") -> list[ServiceRecord]:
        """
        Return records, optionally filtered by ``dis``.

        - ``"all"``: every row.
        - ``"empty"``: rows where qid is NULL or empty string.
        - ``"duplicate"``: rows that share a title or qid with another row.
        """
        try:
            base = db.session.query(self.model)
            if dis == "empty":
                rows = (
                    base.filter(or_(self.model.qid.is_(None), self.model.qid == "")).order_by(self.model.id.asc()).all()
                )
                return rows
            if dis == "duplicate":
                other = aliased(self.model)
                rows = (
                    base.join(
                        other,
                        and_(
                            self.model.id != other.id,
                            or_(
                                self.model.qid == other.qid,
                                self.model.title == other.title,
                            ),
                        ),
                    )
                    .order_by(self.model.id.asc())
                    .distinct()
                    .all()
                )
                return rows
            # default: all
            return base.order_by(self.model.id.asc()).all()

        except Exception as e:
            logger.exception("Failed to list records: %s", e)
            return []

    def list_qid_records(self) -> list[ServiceRecord]:
        """Return all QID records."""
        try:
            return db.session.query(self.model).order_by(self.model.id.asc()).all()
        except Exception as e:
            logger.exception("Failed to list qid records: %s", e)
            return []

    def get_title_to_qid(self) -> dict[str, str]:
        """Retrieve title to QID mapping from database."""
        records = self.list_qid_records()
        return {record.title: record.qid or "" for record in records}

    # ───────────────────────────────────────────────────────────────
    # get by

    def get_by_qid(self, qid: str) -> ServiceRecord | None:
        """Get the first record matching the specified QID string."""
        if not qid:
            return None
        return self.get_by(qid=qid)

    def get_by_title(self, title: str) -> ServiceRecord | None:
        """Get the record matching the specified title."""
        if not title:
            return None
        return self.get_by(title=title)

    def get_by_id(self, qid_id: int) -> ServiceRecord | None:
        """Get a record by its primary key ID."""
        return self.get_record_by_id(qid_id)

    # ───────────────────────────────────────────────────────────────
    # create/update

    def add_or_update(self, title: str, qid: str) -> ServiceRecord | None:
        """Add or update a record for a given title."""
        try:
            validate_or_raise(title, qid)
        except Exception as e:
            logger.error("Invalid title or qid: %s", e)
            return None

        try:
            instance, is_new = self.upsert_by(
                keys={"title": title},
                qid=qid,
            )
            return instance
        except Exception as e:
            logger.exception("Failed to add or update qid: %s", e)
            return None

    def insert(self, title: str, qid: str) -> bool:
        """
        Insert a new row, or fill a missing qid for an existing title.
        """
        try:
            validate_or_raise(title, qid)
        except Exception as e:
            logger.error("Invalid title or qid: %s", e)
            return False

        try:
            existing = self.get_by_title(title)
            if existing:
                if not existing.qid:
                    self.update(existing, qid=qid)
                return True

            orm_obj = self.create(title=title, qid=qid)
            return orm_obj is not None
        except Exception:
            logger.exception("Failed to insert record title=%r qid=%r", title, qid)
            return False

    def update_qid(self, qid_id: int, title: str, qid: str) -> ServiceRecord:
        """Update an existing row by primary key."""
        if not qid_id:
            raise ValueError("qid_id is required")

        validate_or_raise(title, qid)

        orm_obj = self.get_by_id(qid_id)
        if not orm_obj:
            raise ValueError(f"record with ID {qid_id} not found")

        return self.update(orm_obj, title=title, qid=qid)

    # ───────────────────────────────────────────────────────────────
    # delete

    def delete_qid(self, qid_id: int) -> bool:
        return self.delete(qid_id)


__all__ = [
    "BaseQidService",
]
