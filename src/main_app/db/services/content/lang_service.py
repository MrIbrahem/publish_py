"""
SQLAlchemy-based service for managing languages.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import LangRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class LangService(CRUDService[LangRecord]):
    model = LangRecord

    def __init__(self):
        super().__init__(db.session, LangRecord)

    def list_langs(
        self,
    ) -> list[LangRecord]:
        """Return all language records."""
        return list(
            self.list(
                order_by=[LangRecord.lang_id.asc()],
            )
        )

    def get_lang(self, lang_id: int) -> LangRecord | None:
        """Get a language record by ID."""
        orm_obj = self.get(lang_id)
        if not orm_obj:
            logger.warning(f"Language record with ID {lang_id} not found")
            return None
        return orm_obj

    def get_lang_by_code(self, code: str) -> LangRecord | None:
        """Get a language record by code."""
        return self.get_by(code=code)

    def add_lang(
        self,
        code: str,
        autonym: str,
        name: str,
        redirects: list[str] | None = None,
    ) -> LangRecord:
        """Add a new language record."""
        code = code.strip()
        if not code:
            raise ValueError("Language code is required")

        try:
            return self.create(code=code, autonym=autonym, name=name, redirects=redirects)
        except IntegrityError:
            raise ValueError(f"Language '{code}' already exists") from None

    def add_or_update_lang(
        self,
        code: str,
        autonym: str,
        name: str,
        redirects: list[str] | None = None,
    ) -> LangRecord:
        """Add or update a language record."""
        code = code.strip()
        if not code:
            raise ValueError("Language code is required")

        instance, is_new = self.upsert_by(
            keys={"code": code},
            autonym=autonym,
            name=name,
            redirects=redirects,
        )
        return instance


_crud = LangService()
list_langs = _crud.list_langs
get_lang = _crud.get_lang
get_lang_by_code = _crud.get_lang_by_code
add_lang = _crud.add_lang
add_or_update_lang = _crud.add_or_update_lang


__all__ = [
    "list_langs",
    "get_lang",
    "get_lang_by_code",
    "add_lang",
    "add_or_update_lang",
]
