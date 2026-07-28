"""
SQLAlchemy-based service for managing mdwiki revids.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import MdwikiRevidRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class MdwikiRevidService(CRUDService[MdwikiRevidRecord]):
    model = MdwikiRevidRecord

    def __init__(self):
        super().__init__(db.session, MdwikiRevidRecord)

    def list_mdwiki_revids(self) -> list[MdwikiRevidRecord]:
        """Return all mdwiki_revid records."""
        return list(
            self.list(
                order_by=[MdwikiRevidRecord.title.asc()],
            )
        )

    def get_mdwiki_revid_by_title(self, title: str) -> MdwikiRevidRecord | None:
        """Get an mdwiki_revid record by title."""
        return self.get(title)

    def add_mdwiki_revid(self, title: str, revid: int) -> MdwikiRevidRecord:
        """Add a new mdwiki_revid record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        try:
            return self.create(title=title, revid=revid)
        except IntegrityError:
            raise ValueError(f"MDWiki revid for '{title}' already exists") from None

    def add_or_update_mdwiki_revid(self, title: str, revid: int) -> MdwikiRevidRecord | None:
        """Add or update an mdwiki_revid record."""
        title = title.strip()
        if not title:
            raise ValueError("Title is required")

        instance, is_new = self.upsert_by(
            keys={"title": title},
            revid=revid,
        )
        return instance

    def update_mdwiki_revid(self, title: str, revid: int) -> MdwikiRevidRecord | None:
        """Update an mdwiki_revid record."""
        record = self.get_by(title=title)
        if not record:
            raise ValueError(f"MDWiki revid record for '{title}' not found")
        try:
            return self.update(record, revid=revid)
        except Exception as e:
            raise ValueError(f"Failed to update MDWiki revid record for '{title}': {e}") from e

    def get_revid_for_title(self, title: str) -> int | None:
        """Get the revision ID for a title."""
        record = self.get_mdwiki_revid_by_title(title)
        return record.revid if record else None


mdwiki_revid_crud = MdwikiRevidService()

list_mdwiki_revids = mdwiki_revid_crud.list_mdwiki_revids
get_mdwiki_revid_by_title = mdwiki_revid_crud.get_mdwiki_revid_by_title
add_mdwiki_revid = mdwiki_revid_crud.add_mdwiki_revid
add_or_update_mdwiki_revid = mdwiki_revid_crud.add_or_update_mdwiki_revid
update_mdwiki_revid = mdwiki_revid_crud.update_mdwiki_revid
get_revid_for_title = mdwiki_revid_crud.get_revid_for_title

__all__ = [
    "list_mdwiki_revids",
    "get_mdwiki_revid_by_title",
    "add_mdwiki_revid",
    "add_or_update_mdwiki_revid",
    "update_mdwiki_revid",
    "get_revid_for_title",
]
