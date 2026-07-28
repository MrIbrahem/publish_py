"""
SQLAlchemy-based service for managing in-process translations.
"""

from __future__ import annotations

import logging

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import InProcessRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class InProcessService(CRUDService[InProcessRecord]):
    model = InProcessRecord

    def __init__(self):
        super().__init__(db.session, InProcessRecord)

    def list_in_process(self) -> list[InProcessRecord]:
        """Return all in_process records."""
        return list(
            self.list(
                order_by=[InProcessRecord.id.asc()],
            )
        )

    def list_in_process_by_user(self, user: str) -> list[InProcessRecord]:
        """Return in_process records for a specific user."""
        return list(
            self.list(
                filters={"user": user},
                order_by=[InProcessRecord.id.asc()],
            )
        )

    def list_in_process_by_lang(self, lang: str) -> list[InProcessRecord]:
        """Return in_process records for a specific language."""
        return list(
            self.list(
                filters={"lang": lang},
                order_by=[InProcessRecord.id.asc()],
            )
        )

    def get_in_process(self, process_id: int) -> InProcessRecord | None:
        """Get an in_process record by ID."""
        orm_obj = self.get(process_id)
        if not orm_obj:
            logger.warning(f"In-process record with ID {process_id} not found")
            return None
        return orm_obj

    def get_in_process_by_title_user_lang(self, title: str, user: str, lang: str) -> InProcessRecord | None:
        """Get an in_process record by title, user, and language."""
        return self.get_by(title=title, user=user, lang=lang)

    def add_in_process(
        self,
        title: str,
        user: str,
        lang: str,
        cat: str | None = "RTT",
        translate_type: str | None = "lead",
        word: int | None = 0,
    ) -> InProcessRecord:
        """Add a new in_process record."""
        title = title.strip()
        user = user.strip()
        lang = lang.strip()

        if not title:
            raise ValueError("Title is required")
        if not user:
            raise ValueError("User is required")
        if not lang:
            raise ValueError("Language is required")

        try:
            return self.create(
                title=title,
                user=user,
                lang=lang,
                cat=cat,
                translate_type=translate_type,
                word=word,
                add_date=func.now(),
            )
        except IntegrityError:
            raise ValueError(f"In-process record for '{title}' by '{user}' in '{lang}' already exists") from None

    def update_in_process(self, process_id: int, **kwargs) -> InProcessRecord:
        """Update an in_process record."""
        return self.update_or_404(process_id, **kwargs)

    def delete_in_process_by_title_user_lang(self, title: str, user: str, lang: str) -> bool:
        """Delete an in_process record by title, user, and language."""
        record = self.get_by(title=title, user=user, lang=lang)
        if not record:
            return False
        return self.delete(record.id)

    def is_in_process(self, title: str, user: str, lang: str) -> bool:
        """Check if a translation is in process."""
        record = self.get_in_process_by_title_user_lang(title, user, lang)
        return record is not None

    def get_in_process_counts_by_user(self) -> list[dict]:
        """Get count of in-process translations per user, sorted by count descending."""
        results = (
            self.session.query(
                InProcessRecord.user,
                db.func.count(InProcessRecord.id).label("article_count"),
            )
            .group_by(InProcessRecord.user)
            .order_by(db.func.count(InProcessRecord.id).desc())
            .all()
        )
        return [{"user": row.user, "article_count": row.article_count} for row in results]


_crud = InProcessService()
list_in_process = _crud.list_in_process
list_in_process_by_user = _crud.list_in_process_by_user
list_in_process_by_lang = _crud.list_in_process_by_lang
get_in_process = _crud.get_in_process
get_in_process_by_title_user_lang = _crud.get_in_process_by_title_user_lang
add_in_process = _crud.add_in_process
update_in_process = _crud.update_in_process
delete_in_process_by_title_user_lang = _crud.delete_in_process_by_title_user_lang
is_in_process = _crud.is_in_process
get_in_process_counts_by_user = _crud.get_in_process_counts_by_user

__all__ = [
    "list_in_process",
    "list_in_process_by_user",
    "list_in_process_by_lang",
    "get_in_process",
    "get_in_process_by_title_user_lang",
    "add_in_process",
    "update_in_process",
    "delete_in_process_by_title_user_lang",
    "is_in_process",
    "get_in_process_counts_by_user",
]
