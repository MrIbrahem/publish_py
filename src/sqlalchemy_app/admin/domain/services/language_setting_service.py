"""
SQLAlchemy-based service for managing language settings.
"""

from __future__ import annotations

import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from .....db_models.admin_models import LanguageSettingRecord
from ....shared.domain.engine import get_session
from ..models import _LanguageSettingRecord

logger = logging.getLogger(__name__)


def list_language_settings() -> List[LanguageSettingRecord]:
    """Return all language setting records."""
    with get_session() as session:
        orm_objs = session.query(_LanguageSettingRecord).order_by(_LanguageSettingRecord.id.asc()).all()
        return [LanguageSettingRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_language_setting(setting_id: int) -> LanguageSettingRecord | None:
    """Get a language setting record by ID."""
    with get_session() as session:
        orm_obj = session.query(_LanguageSettingRecord).filter(_LanguageSettingRecord.id == setting_id).first()
        if not orm_obj:
            logger.warning(f"Language setting record with ID {setting_id} not found")
            return None
        return LanguageSettingRecord(**orm_obj.to_dict())


def get_language_setting_by_code(lang_code: str) -> LanguageSettingRecord | None:
    """Get a language setting record by language code."""
    with get_session() as session:
        orm_obj = session.query(_LanguageSettingRecord).filter(_LanguageSettingRecord.lang_code == lang_code).first()
        if not orm_obj:
            return None
        return LanguageSettingRecord(**orm_obj.to_dict())


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

    with get_session() as session:
        orm_obj = _LanguageSettingRecord(
            lang_code=lang_code,
            move_dots=move_dots,
            expend=expend,
            add_en_lang=add_en_lang,
        )
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Language setting for '{lang_code}' already exists") from None

        session.refresh(orm_obj)
        return LanguageSettingRecord(**orm_obj.to_dict())


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

    with get_session() as session:
        orm_obj = session.query(_LanguageSettingRecord).filter(_LanguageSettingRecord.lang_code == lang_code).first()
        if orm_obj:
            orm_obj.move_dots = move_dots
            orm_obj.expend = expend
            orm_obj.add_en_lang = add_en_lang
        else:
            orm_obj = _LanguageSettingRecord(
                lang_code=lang_code,
                move_dots=move_dots,
                expend=expend,
                add_en_lang=add_en_lang,
            )
            session.add(orm_obj)

        session.commit()
        session.refresh(orm_obj)
        return LanguageSettingRecord(**orm_obj.to_dict())


def update_language_setting(setting_id: int, **kwargs) -> LanguageSettingRecord:
    """Update a language setting record."""
    with get_session() as session:
        orm_obj = session.query(_LanguageSettingRecord).filter(_LanguageSettingRecord.id == setting_id).first()
        if not orm_obj:
            raise ValueError(f"Language setting record with ID {setting_id} not found")

        if not kwargs:
            return LanguageSettingRecord(**orm_obj.to_dict())

        for key, value in kwargs.items():
            if hasattr(orm_obj, key):
                setattr(orm_obj, key, value)

        session.commit()
        session.refresh(orm_obj)
        return LanguageSettingRecord(**orm_obj.to_dict())


def delete_language_setting(setting_id: int) -> LanguageSettingRecord:
    """Delete a language setting record by ID."""
    with get_session() as session:
        orm_obj = session.query(_LanguageSettingRecord).filter(_LanguageSettingRecord.id == setting_id).first()
        if not orm_obj:
            raise ValueError(f"Language setting record with ID {setting_id} not found")

        record = LanguageSettingRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


__all__ = [
    "list_language_settings",
    "get_language_setting",
    "get_language_setting_by_code",
    "add_language_setting",
    "add_or_update_language_setting",
    "update_language_setting",
    "delete_language_setting",
]
