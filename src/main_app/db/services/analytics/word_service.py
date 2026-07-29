"""
SQLAlchemy-based service for managing words.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import WordRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class WordService(CRUDService[WordRecord]):
    model = WordRecord

    def __init__(self):
        super().__init__(db.session, WordRecord)

    def list_words(self) -> list[WordRecord]:
        """Return all word records."""
        return self.list_all(
            order_by=[WordRecord.w_id.asc()],
        )

    def get_word(self, word_id: int) -> WordRecord | None:
        """Get a word record by ID."""
        return self.get(word_id)

    def get_word_by_title(self, title: str) -> WordRecord | None:
        """Get a word record by title."""
        return self.get_by(w_title=title)

    def add_word(
        self,
        w_title: str,
        w_lead_words: int | None = None,
        w_all_words: int | None = None,
    ) -> WordRecord:
        """Add a new word record."""
        w_title = w_title.strip()
        if not w_title:
            raise ValueError("Title is required")

        try:
            return self.create(w_title=w_title, w_lead_words=w_lead_words, w_all_words=w_all_words)
        except IntegrityError:
            raise ValueError(f"Word count for '{w_title}' already exists") from None

    def add_or_update_word(
        self,
        w_title: str,
        w_lead_words: int | None = None,
        w_all_words: int | None = None,
    ) -> WordRecord:
        """Add or update a word record."""
        w_title = w_title.strip()
        if not w_title:
            raise ValueError("Title is required")

        instance, is_new = self.upsert_by(
            keys={"w_title": w_title},
            w_lead_words=w_lead_words,
            w_all_words=w_all_words,
        )
        return instance

    def update_word(self, word_id: int, **kwargs) -> WordRecord:
        """Update a word record."""
        return self.update_or_404(word_id, **kwargs)

    def get_word_counts_for_title(self, title: str) -> tuple[int | None, int | None]:
        """Get lead and all word counts for a title."""
        record = self.get_word_by_title(title)
        if record:
            return record.w_lead_words, record.w_all_words
        return None, None


__all__ = [
    "WordService",
]
