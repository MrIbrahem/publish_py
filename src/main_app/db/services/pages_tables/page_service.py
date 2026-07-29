"""
SQLAlchemy-based service for managing pages and page targets.
"""

from __future__ import annotations

import logging
from sqlalchemy import func, or_

from .pages_shared_service import BasePagesService

from ....extensions import db
from ...models import PageRecord
from ..analytics import WordService

logger = logging.getLogger(__name__)

ModelT = PageRecord

class PagesService(BasePagesService):
    def __init__(self):
        self.word_service = WordService()
        super().__init__(PageRecord, db.session)

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
            lead_words, all_words = self.word_service.get_word_counts_for_title(title)
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
            self.session.query(self.model).filter(
                self.model.user == user,
                self.model.title == title,
                self.model.lang == lang,
                or_(self.model.target == "", self.model.target.is_(None)),
            ).update(
                {self.model.target: target, self.model.pupdate: pupdate, "word": word},
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
            self.session.query(self.model)
            .filter(
                self.model.title == title,
                self.model.lang == lang,
                self.model.user == user,
                self.model.target == target,
            )
            .first()
        )
        return found is not None


__all__ = [
    "PagesService",
]
