"""
SQLAlchemy-based service for managing pages_users and page targets.

The 2 files following is the same, but:
- user_page_service.py targets ``pages_users`` table.
- page_service.py targets ``pages`` table.

TODO: use pages_shared_service.py
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import UserPageRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)

ModelT = UserPageRecord


class UserPagesService(CRUDService[ModelT]):
    model = ModelT

    def __init__(self):
        super().__init__(db.session, ModelT)
        self.model = ModelT

    def list_pages(self) -> list[ModelT]:
        """Return all pages."""
        return list(
            self.list(
                order_by=[self.model.id.asc()],
            )
        )

    def list_pages_by_lang_cat(self, lang: str, cat: str) -> list[ModelT]:
        """Return pages filtered by language and category."""
        return list(self.list(filters={"lang": lang, "cat": cat}))

    def list_translated(self, lang: str = "All", limit: int = 500, offset: int = 0) -> list[ModelT]:
        """Return translated pages (target not empty) optionally filtered by language."""
        query = self.session.query(self.model).filter(self.model.target.isnot(None), self.model.target != "")
        if lang and lang.lower() != "all":
            query = query.filter(self.model.lang == lang)
        return query.order_by(self.model.id.desc()).limit(limit).offset(offset).all()

    def count_translated(self, lang: str = "All") -> int:
        """Return total count of translated pages, optionally filtered by language."""
        query = self.session.query(func.count(self.model.id)).filter(
            self.model.target.isnot(None), self.model.target != ""
        )
        if lang and lang.lower() != "all":
            query = query.filter(self.model.lang == lang)
        return int(query.scalar() or 0)

    def get_by_id(self, page_id: int) -> ModelT | None:
        """Return a single page row by id, or None when missing."""
        return self.get(page_id)

    def get_page_by_id(self, page_id: int) -> ModelT | None:
        """Return a single page row by id, or None when missing."""
        return self.get(page_id)

    def add_page(
        self,
        sourcetitle: str,
        translate_type: str,
        cat: str,
        lang: str,
        user: str,
        target: str,
        mdwiki_revid: int | None = None,
        word: int = 0,
    ) -> ModelT:
        """Add a page and return the created record."""
        if not sourcetitle:
            raise ValueError("Title is required")
        try:
            return self.create(
                title=sourcetitle,
                word=word,
                translate_type=translate_type,
                cat=cat,
                lang=lang,
                user=user,
                pupdate=func.current_date(),
                target=target,
                mdwiki_revid=mdwiki_revid,
            )
        except IntegrityError as e:
            logger.error(f"Failed to add page (integrity error): {e}")
            raise ValueError(f"Page with title '{sourcetitle}' already exists") from e
        except Exception as e:
            logger.error(f"Failed to add page: {e}")
            raise

    def insert_page_target(
        self,
        sourcetitle: str,
        translate_type: str,
        cat: str,
        lang: str,
        user: str,
        target: str,
        mdwiki_revid: int | None = None,
        word: int = 0,
    ) -> bool:
        """Insert a page target record and return success status."""
        try:
            self.add_page(
                sourcetitle=sourcetitle,
                translate_type=translate_type,
                cat=cat,
                lang=lang,
                user=user,
                target=target,
                mdwiki_revid=mdwiki_revid,
                word=word,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to insert page target: {e}")
            return False

    def update_page(
        self,
        page_id: int,
        title: str,
        target: str,
        **kwargs: Any,
    ) -> ModelT | None:
        """Update page."""
        try:
            data = {"title": title, "target": target, **kwargs}
            return self.update_by_id(page_id, data)
        except ValueError as exc:
            raise LookupError(f"Page id {page_id} was not found") from exc

    def update_row_by_id(
        self,
        page_id: int,
        title: str,
        target: str,
        **kwargs: Any,
    ) -> ModelT | None:
        """Update page."""
        return self.update_page(page_id, title, target, **kwargs)

    def set_target(
        self,
        record: ModelT,
        target: str,
    ) -> bool:
        """ """
        try:
            self.update(record, target=target, pupdate=datetime.now().strftime("%Y-%m-%d"))
            return True
        except Exception:
            logger.exception("Failed to update page target")
            return False

    def find_page_record(
        self,
        title: str,
        lang: str,
        user: str,
    ) -> ModelT | None:
        """
        Check if record exists
        """
        return self.get_by(title=title, lang=lang, user=user)


__all__ = [
    "UserPagesService",
]
