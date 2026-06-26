"""
SQLAlchemy-based service for managing language settings.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import LanguageSettingRecord

logger = logging.getLogger(__name__)


def list_language_settings() -> List[LanguageSettingRecord]:
    """Return all language setting records."""
    orm_objs = db.session.query(LanguageSettingRecord).order_by(LanguageSettingRecord.id.asc()).all()
    return orm_objs


def get_language_setting(setting_id: int) -> LanguageSettingRecord | None:
    """Get a language setting record by ID."""
    orm_obj = db.session.get(LanguageSettingRecord, setting_id)
    if not orm_obj:
        logger.warning(f"Language setting record with ID {setting_id} not found")
        return None
    return orm_obj


def get_language_setting_by_code(lang_code: str) -> LanguageSettingRecord | None:
    """Get a language setting record by language code."""
    orm_obj = db.session.query(LanguageSettingRecord).filter(LanguageSettingRecord.lang_code == lang_code).first()
    if not orm_obj:
        return None
    return orm_obj


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

    orm_obj = LanguageSettingRecord(
        lang_code=lang_code,
        move_dots=move_dots,
        expend=expend,
        add_en_lang=add_en_lang,
    )
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Language setting for '{lang_code}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


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

    orm_obj = db.session.query(LanguageSettingRecord).filter(LanguageSettingRecord.lang_code == lang_code).first()
    if orm_obj:
        orm_obj.move_dots = move_dots
        orm_obj.expend = expend
        orm_obj.add_en_lang = add_en_lang
    else:
        orm_obj = LanguageSettingRecord(
            lang_code=lang_code,
            move_dots=move_dots,
            expend=expend,
            add_en_lang=add_en_lang,
        )
        db.session.add(orm_obj)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def update_language_setting(setting_id: int, **kwargs) -> LanguageSettingRecord:
    """Update a language setting record."""
    orm_obj = db.session.get(LanguageSettingRecord, setting_id)
    if not orm_obj:
        raise ValueError(f"Language setting record with ID {setting_id} not found")

    if not kwargs:
        return orm_obj

    for key, value in kwargs.items():
        if hasattr(orm_obj, key):
            setattr(orm_obj, key, value)

    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


__all__ = [
    "list_language_settings",
    "get_language_setting",
    "get_language_setting_by_code",
    "add_language_setting",
    "add_or_update_language_setting",
    "update_language_setting",
]
