"""
SQLAlchemy-based service for managing settings.
"""

from __future__ import annotations

import logging
from typing import Any, List

from sqlalchemy.exc import IntegrityError

from ...sqlalchemy_models import SettingRecord
from ..core.extensions import db

logger = logging.getLogger(__name__)


def list_settings() -> List[SettingRecord]:
    """Return all setting records."""
    orm_objs = db.session.query(SettingRecord).order_by(SettingRecord.id.asc()).all()
    return orm_objs


def get_setting(setting_id: int) -> SettingRecord | None:
    """Get a setting record by ID."""
    orm_obj = db.session.query(SettingRecord).filter(SettingRecord.id == setting_id).first()
    if not orm_obj:
        logger.warning(f"Setting record with ID {setting_id} not found")
        return None
    return orm_obj


def get_setting_by_key(key: str) -> SettingRecord | None:
    """Get a setting record by key."""
    orm_obj = db.session.query(SettingRecord).filter(SettingRecord.key == key).first()
    if not orm_obj:
        return None
    return orm_obj


def add_setting(
    key: str,
    title: str,
    value_type: str = "boolean",
    value: Any = None,
) -> SettingRecord:
    """Add a new setting record."""
    key = key.strip()
    title = title.strip()
    if not key:
        raise ValueError("Key is required")
    if not title:
        raise ValueError("Title is required")

    orm_obj = SettingRecord(
        key=key,
        title=title,
        value_type=value_type,
        value=str(value) if value is not None else None,
    )
    db.session.add(orm_obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"Setting with key '{key}' already exists") from None

    db.session.refresh(orm_obj)
    return orm_obj


def update_value(setting_id: int, value: Any) -> SettingRecord:
    """Update a setting record value."""
    orm_obj: SettingRecord = db.session.query(SettingRecord).filter(SettingRecord.id == setting_id).first()
    if not orm_obj:
        raise ValueError(f"Setting record with ID {setting_id} not found")

    orm_obj.value = value  # str(value) if value is not None else None
    db.session.commit()
    db.session.refresh(orm_obj)
    return orm_obj


def delete_setting(setting_id: int) -> SettingRecord:
    """Delete a setting record by ID."""
    orm_obj = db.session.query(SettingRecord).filter(SettingRecord.id == setting_id).first()
    if not orm_obj:
        raise ValueError(f"Setting record with ID {setting_id} not found")

    record = SettingRecord(**orm_obj.to_dict())
    db.session.delete(orm_obj)
    db.session.commit()
    return record


__all__ = [
    "list_settings",
    "get_setting",
    "get_setting_by_key",
    "add_setting",
    "update_value",
    "delete_setting",
]
