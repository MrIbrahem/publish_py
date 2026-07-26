"""
SQLAlchemy-based service for managing language settings.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import LanguageSettingRecord
from ..base import CRUDService

logger = logging.getLogger(__name__)


class LanguageSettingService(CRUDService[LanguageSettingRecord, int]):
    model = LanguageSettingRecord


language_setting_crud = LanguageSettingService(db.session)


def list_language_settings() -> list[LanguageSettingRecord]:
    """Return all language setting records."""
    return list(language_setting_crud.list(order_by=[LanguageSettingRecord.id.asc()]))


def get_language_setting(setting_id: int) -> LanguageSettingRecord | None:
    """Get a language setting record by ID."""
    orm_obj = language_setting_crud.get(setting_id)
    if not orm_obj:
        logger.warning(f"Language setting record with ID {setting_id} not found")
        return None
    return orm_obj


def get_language_setting_by_code(lang_code: str) -> LanguageSettingRecord | None:
    """Get a language setting record by language code."""
    return language_setting_crud.get_by(lang_code=lang_code)


def add_language_setting(
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
        return language_setting_crud.create(
            lang_code=lang_code,
            move_dots=move_dots,
            expend=expend,
            add_en_lang=add_en_lang,
        )
    except IntegrityError:
        raise ValueError(f"Language setting for '{lang_code}' already exists") from None


def add_or_update_language_setting(
    lang_code: str,
    move_dots: int = 0,
    expend: int = 0,
    add_en_lang: int = 0,
) -> LanguageSettingRecord:
    """Add or update a language setting record."""
    lang_code = lang_code.strip()
    if not lang_code:
        raise ValueError("Language code is required")

    return language_setting_crud.upsert(
        keys={"lang_code": lang_code},
        move_dots=move_dots,
        expend=expend,
        add_en_lang=add_en_lang,
    )


def update_language_setting(setting_id: int, **kwargs) -> LanguageSettingRecord:
    """Update a language setting record."""
    if not kwargs:
        orm_obj = language_setting_crud.get(setting_id)
        if not orm_obj:
            raise ValueError(f"Language setting record with ID {setting_id} not found")
        return orm_obj

    try:
        return language_setting_crud.update(setting_id, **kwargs)
    except ValueError as exc:
        raise ValueError(f"Language setting record with ID {setting_id} not found") from exc


__all__ = [
    "list_language_settings",
    "get_language_setting",
    "get_language_setting_by_code",
    "add_language_setting",
    "add_or_update_language_setting",
    "update_language_setting",
]
