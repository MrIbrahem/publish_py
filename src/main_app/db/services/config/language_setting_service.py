"""
SQLAlchemy-based service for managing language settings.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import LanguageSettingRecord
from ..crud_service import CRUDService

logger = logging.getLogger(__name__)


class LanguageSettingService(CRUDService[LanguageSettingRecord]):
    model = LanguageSettingRecord

    def __init__(self):
        super().__init__(db.session, LanguageSettingRecord)

    def list_language_settings(self) -> list[LanguageSettingRecord]:
        """Return all language setting records."""
        return list(
            self.list(
                order_by=[LanguageSettingRecord.id.asc()],
            )
        )

    def get_language_setting(self, setting_id: int) -> LanguageSettingRecord | None:
        """Get a language setting record by ID."""
        orm_obj = self.get(setting_id)
        if not orm_obj:
            logger.warning(f"Language setting record with ID {setting_id} not found")
            return None
        return orm_obj

    def get_language_setting_by_code(self, lang_code: str) -> LanguageSettingRecord | None:
        """Get a language setting record by language code."""
        return self.get_by(lang_code=lang_code)

    def add_language_setting(
        self,
        lang_code: str,
        move_dots: int = 0,
        expend: int = 0,
        add_en_lang: int = 0,
    ) -> LanguageSettingRecord:
        """Add a new language setting record."""
        lang_code = lang_code.strip()
        if not lang_code:
            raise ValueError("Language code is required")

        try:
            return self.create(
                lang_code=lang_code,
                move_dots=move_dots,
                expend=expend,
                add_en_lang=add_en_lang,
            )
        except IntegrityError:
            raise ValueError(f"Language setting for '{lang_code}' already exists") from None

    def add_or_update_language_setting(
        self,
        lang_code: str,
        move_dots: int = 0,
        expend: int = 0,
        add_en_lang: int = 0,
    ) -> LanguageSettingRecord:
        """Add or update a language setting record."""
        lang_code = lang_code.strip()
        if not lang_code:
            raise ValueError("Language code is required")

        instance, is_new = self.upsert_by(
            keys={"lang_code": lang_code},
            move_dots=move_dots,
            expend=expend,
            add_en_lang=add_en_lang,
        )
        return instance

    def update_language_setting(self, setting_id: int, **kwargs) -> LanguageSettingRecord:
        """Update a language setting record."""
        return self.update_or_404(setting_id, **kwargs)

__all__ = [
    "LanguageSettingService",
]
