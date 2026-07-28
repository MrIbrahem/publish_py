"""
SQLAlchemy-based service for managing pages and page targets.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import PageRecord
from ..analytics.word_service import get_word_counts_for_title
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class PagesService(CRUDService[PageRecord]):
    model = PageRecord

    def __init__(self):
        super().__init__(db.session, PageRecord)

    def list_translated(self, lang: str = "All", limit: int = 500, offset: int = 0) -> list[PageRecord]:
        """Return translated pages (target not empty) optionally filtered by language."""
        query = self.session.query(PageRecord).filter(PageRecord.target.isnot(None), PageRecord.target != "")
        if lang and lang.lower() != "all":
            query = query.filter(PageRecord.lang == lang)
        return query.order_by(PageRecord.id.desc()).limit(limit).offset(offset).all()

    def count_translated(self, lang: str = "All") -> int:
        """Return total count of translated pages, optionally filtered by language."""
        query = self.session.query(func.count(PageRecord.id)).filter(
            PageRecord.target.isnot(None), PageRecord.target != ""
        )
        if lang and lang.lower() != "all":
            query = query.filter(PageRecord.lang == lang)
        return int(query.scalar() or 0)

    def get_by_id(self, page_id: int) -> PageRecord | None:
        """Return a single page row by id, or None when missing."""
        return self.get(page_id)

    def get_page_by_id(self, page_id: int) -> PageRecord | None:
        """Return a single page row by id, or None when missing."""
        return self.get(page_id)

    def list_pages(self) -> list[PageRecord]:
        """Return all pages."""
        return list(
            self.list(
                order_by=[PageRecord.id.asc()],
            )
        )

    def list_pages_by_lang_cat(self, lang: str, cat: str) -> list[PageRecord]:
        """Return pages filtered by language and category."""
        return list(self.list(filters={"lang": lang, "cat": cat}))

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
    ) -> PageRecord:
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
    ) -> PageRecord | None:
        """Update page."""
        try:
            data = {"title": title, "target": target, **kwargs}
            return self.update_by_id(page_id, data)
        except ValueError as exc:
            raise LookupError(f"Page id {page_id} was not found") from exc

    def set_page_target(
        self,
        record: PageRecord,
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
    ) -> PageRecord | None:
        """
        Check if record exists
        """
        return self.get_by(title=title, lang=lang, user=user)

    def add_translate_row_to_db(
        self,
        title: str,
        translate_type: str,
        cat: str,
        lang: str,
        user: str,
        target: str,
        pupdate: str,
        word: int = 0,
    ) -> bool:
        """Mirror of PHP add_pages_to_db + insert_to_pages.

        Replaces ``_`` with `` `` in string values, UPDATEs rows where target is
        empty, then INSERTs a new row if no matching title+lang+user exists.
        """
        translate_type = translate_type or "lead"
        cat = cat or "RTT"

        if word == 0:
            lead_words, all_words = get_word_counts_for_title(title)
            if translate_type == "all":
                word = all_words or 0
            else:
                word = lead_words or 0

        title = title.replace("_", " ")
        user = user.replace("_", " ")
        target = target.replace("_", " ")
        cat = cat.replace("_", " ")
        lang = lang.replace("_", " ")
        pupdate = pupdate.replace("_", " ")

        try:
            self.session.query(PageRecord).filter(
                PageRecord.user == user,
                PageRecord.title == title,
                PageRecord.lang == lang,
                or_(PageRecord.target == "", PageRecord.target.is_(None)),
            ).update(
                {PageRecord.target: target, PageRecord.pupdate: pupdate, "word": word},
                synchronize_session=False,
            )
        except Exception:
            logger.exception("Failed to update existing page target")
            self.session.rollback()
            return False

        existing = self.get_by(title=title, lang=lang, user=user)

        if not existing:
            try:
                self.create(
                    title=title,
                    word=word,
                    translate_type=translate_type,
                    cat=cat,
                    lang=lang,
                    user=user,
                    target=target,
                    pupdate=pupdate,
                    date=func.current_date(),
                )
            except Exception:
                logger.exception("Failed to insert new page")
                return False

        found = (
            self.session.query(PageRecord)
            .filter(
                PageRecord.title == title, PageRecord.lang == lang, PageRecord.user == user, PageRecord.target == target
            )
            .first()
        )
        return found is not None


_crud = PagesService()

list_translated = _crud.list_translated
count_translated = _crud.count_translated
get_by_id = _crud.get_by_id
get_page_by_id = _crud.get_page_by_id
list_pages = _crud.list_pages
list_pages_by_lang_cat = _crud.list_pages_by_lang_cat
add_page = _crud.add_page
insert_page_target = _crud.insert_page_target
update_page = _crud.update_page
set_page_target = _crud.set_page_target
find_page_record = _crud.find_page_record
add_translate_row_to_db = _crud.add_translate_row_to_db

__all__ = [
    "get_page_by_id",
    "set_page_target",
    "find_page_record",
    "list_pages",
    "list_pages_by_lang_cat",
    "add_page",
    "update_page",
    "insert_page_target",
    "add_translate_row_to_db",
]
