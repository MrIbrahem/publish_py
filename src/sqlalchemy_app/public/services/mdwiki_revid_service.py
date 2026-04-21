"""
SQLAlchemy-based service for managing mdwiki revids.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ...sqlalchemy_models import MdwikiRevidRecord
from ...shared.engine import get_session
from ...sqlalchemy_models import _MdwikiRevidRecord

logger = logging.getLogger(__name__)


def list_mdwiki_revids() -> List[MdwikiRevidRecord]:
    """Return all mdwiki_revid records."""
    with get_session() as session:
        orm_objs = session.query(_MdwikiRevidRecord).order_by(_MdwikiRevidRecord.title.asc()).all()
        return [MdwikiRevidRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_mdwiki_revid_by_title(title: str) -> MdwikiRevidRecord | None:
    """Get an mdwiki_revid record by title."""
    with get_session() as session:
        orm_obj = session.query(_MdwikiRevidRecord).filter(_MdwikiRevidRecord.title == title).first()
        if not orm_obj:
            return None
        return MdwikiRevidRecord(**orm_obj.to_dict())


def add_mdwiki_revid(title: str, revid: int) -> MdwikiRevidRecord:
    """Add a new mdwiki_revid record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = _MdwikiRevidRecord(title=title, revid=revid)
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"MDWiki revid for '{title}' already exists") from None

        session.refresh(orm_obj)
        return MdwikiRevidRecord(**orm_obj.to_dict())


def add_or_update_mdwiki_revid(title: str, revid: int) -> MdwikiRevidRecord:
    """Add or update an mdwiki_revid record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    with get_session() as session:
        orm_obj = session.query(_MdwikiRevidRecord).filter(_MdwikiRevidRecord.title == title).first()
        if orm_obj:
            orm_obj.revid = revid
        else:
            orm_obj = _MdwikiRevidRecord(title=title, revid=revid)
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return MdwikiRevidRecord(**orm_obj.to_dict())


def update_mdwiki_revid(title: str, revid: int) -> MdwikiRevidRecord:
    """Update an mdwiki_revid record."""
    with get_session() as session:
        orm_obj = session.query(_MdwikiRevidRecord).filter(_MdwikiRevidRecord.title == title).first()
        if not orm_obj:
            raise ValueError(f"MDWiki revid record for '{title}' not found")

        orm_obj.revid = revid
        session.commit()
        session.refresh(orm_obj)
        return MdwikiRevidRecord(**orm_obj.to_dict())


def delete_mdwiki_revid(title: str) -> MdwikiRevidRecord:
    """Delete an mdwiki_revid record by title."""
    with get_session() as session:
        orm_obj = session.query(_MdwikiRevidRecord).filter(_MdwikiRevidRecord.title == title).first()
        if not orm_obj:
            raise ValueError(f"MDWiki revid record for '{title}' not found")

        record = MdwikiRevidRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


def get_revid_for_title(title: str) -> int | None:
    """Get the revision ID for a title."""
    record = get_mdwiki_revid_by_title(title)
    return record.revid if record else None


__all__ = [
    "list_mdwiki_revids",
    "get_mdwiki_revid_by_title",
    "add_mdwiki_revid",
    "add_or_update_mdwiki_revid",
    "update_mdwiki_revid",
    "delete_mdwiki_revid",
    "get_revid_for_title",
]
