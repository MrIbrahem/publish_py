"""
SQLAlchemy-based service for managing settings.
"""

from __future__ import annotations

import logging
from typing import Any, List

from sqlalchemy.exc import IntegrityError

from ....shared.domain.engine import get_session
from ...domain_models import SettingRecord
from ..models import _SettingRecord

logger = logging.getLogger(__name__)


def list_settings() -> List[SettingRecord]:
    """Return all setting records."""
    with get_session() as session:
        orm_objs = session.query(_SettingRecord).order_by(_SettingRecord.id.asc()).all()
        return [SettingRecord(**orm_obj.to_dict()) for orm_obj in orm_objs]


def get_setting(setting_id: int) -> SettingRecord | None:
    """Get a setting record by ID."""
    with get_session() as session:
        orm_obj = session.query(_SettingRecord).filter(_SettingRecord.id == setting_id).first()
        if not orm_obj:
            logger.warning(f"Setting record with ID {setting_id} not found")
            return None
        return SettingRecord(**orm_obj.to_dict())


def get_setting_by_key(key: str) -> SettingRecord | None:
    """Get a setting record by key."""
    with get_session() as session:
        orm_obj = session.query(_SettingRecord).filter(_SettingRecord.key == key).first()
        if not orm_obj:
            return None
        return SettingRecord(**orm_obj.to_dict())


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

    with get_session() as session:
        orm_obj = _SettingRecord(
            key=key,
            title=title,
            value_type=value_type,
            value=str(value) if value is not None else None,
        )
        session.add(orm_obj)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Setting with key '{key}' already exists") from None

        session.refresh(orm_obj)
        return SettingRecord(**orm_obj.to_dict())


def update_value(setting_id: int, value: Any) -> SettingRecord:
    """Update a setting record value."""
    with get_session() as session:
        orm_obj = session.query(_SettingRecord).filter(_SettingRecord.id == setting_id).first()
        if not orm_obj:
            raise ValueError(f"Setting record with ID {setting_id} not found")

        orm_obj.value = str(value) if value is not None else None
        session.commit()
        session.refresh(orm_obj)
        return SettingRecord(**orm_obj.to_dict())


def delete_setting(setting_id: int) -> SettingRecord:
    """Delete a setting record by ID."""
    with get_session() as session:
        orm_obj = session.query(_SettingRecord).filter(_SettingRecord.id == setting_id).first()
        if not orm_obj:
            raise ValueError(f"Setting record with ID {setting_id} not found")

        record = SettingRecord(**orm_obj.to_dict())
        session.delete(orm_obj)
        session.commit()
        return record


__all__ = [
    "list_settings",
    "get_setting",
    "get_setting_by_key",
    "add_setting",
    "update_value",
    "delete_setting",
]
