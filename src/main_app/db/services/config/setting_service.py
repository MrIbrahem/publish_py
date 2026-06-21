"""
SQLAlchemy-based service for managing settings.
"""

from __future__ import annotations

import logging
from typing import Any, List

from sqlalchemy.exc import IntegrityError

from ....shared.core.extensions import db
from ...models import SettingRecord

logger = logging.getLogger(__name__)


def list_settings() -> List[SettingRecord]:
    """Return all setting records."""
    orm_objs = db.session.query(SettingRecord).order_by(SettingRecord.id.asc()).all()
    return orm_objs


def get_setting(setting_id: int) -> SettingRecord | None:
    """Get a setting record by ID."""
    orm_obj = db.session.get(SettingRecord, setting_id)
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
    value: Any | None = None,
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
    """Update a setting record value.

    Normalizes the input identically to ``add_setting`` so the persisted
    type stays consistent across creation and updates: non-``None`` values
    are coerced to ``str``; ``None`` is stored as ``None``.
    """
    orm_obj: SettingRecord = db.session.get(SettingRecord, setting_id)
    if not orm_obj:
        raise ValueError(f"Setting record with ID {setting_id} not found")

    orm_obj.value = str(value) if value is not None else None
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    db.session.refresh(orm_obj)
    return orm_obj


def delete_setting(setting_id: int) -> bool:
    """Delete a setting record by ID."""
    # orm_obj = db.session.query(SettingRecord).filter(SettingRecord.id == setting_id).first()
    orm_obj = db.session.get(SettingRecord, setting_id)
    if not orm_obj:
        raise ValueError(f"Setting record with ID {setting_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(SettingRecord, setting_id)
    return deleted is None


__all__ = [
    "list_settings",
    "get_setting",
    "get_setting_by_key",
    "add_setting",
    "update_value",
    "delete_setting",
]
