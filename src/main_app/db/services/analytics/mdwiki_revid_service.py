"""
SQLAlchemy-based service for managing mdwiki revids.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import MdwikiRevidRecord

logger = logging.getLogger(__name__)


def list_mdwiki_revids() -> List[MdwikiRevidRecord]:
    """Return all mdwiki_revid records."""
    orm_objs = db.session.query(MdwikiRevidRecord).order_by(MdwikiRevidRecord.title.asc()).all()
    return orm_objs


def get_mdwiki_revid_by_title(title: str) -> MdwikiRevidRecord | None:
    """Get an mdwiki_revid record by title."""
    orm_obj = db.session.get(MdwikiRevidRecord, title)
    if not orm_obj:
        return None
    return orm_obj


def add_mdwiki_revid(title: str, revid: int) -> MdwikiRevidRecord:
    """Add a new mdwiki_revid record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    orm_obj = MdwikiRevidRecord(title=title, revid=revid)
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"MDWiki revid for '{title}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def add_or_update_mdwiki_revid(title: str, revid: int) -> MdwikiRevidRecord:
    """Add or update an mdwiki_revid record."""
    title = title.strip()
    if not title:
        raise ValueError("Title is required")

    orm_obj = db.session.get(MdwikiRevidRecord, title)
    if orm_obj:
        orm_obj.revid = revid
    else:
        orm_obj = MdwikiRevidRecord(title=title, revid=revid)
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_mdwiki_revid(title: str, revid: int) -> MdwikiRevidRecord:
    """Update an mdwiki_revid record."""
    orm_obj = db.session.get(MdwikiRevidRecord, title)
    if not orm_obj:
        raise ValueError(f"MDWiki revid record for '{title}' not found")

    orm_obj.revid = revid
    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


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
    "get_revid_for_title",
]
