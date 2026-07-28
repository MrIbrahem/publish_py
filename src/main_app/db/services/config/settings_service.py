"""
SQLAlchemy-based service for managing settings.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ...models import SettingRecord
from ..crud_service import CRUDService
from ..utils import db_guard

logger = logging.getLogger(__name__)


class SettingService(CRUDService[SettingRecord]):
    model = SettingRecord

    def __init__(self):
        super().__init__(db.session, SettingRecord)


setting_crud = SettingService()


def _serialize_value(value: Any, value_type: str) -> str | None:
    if value is None:
        return None
    if value_type == "boolean":
        return "true" if value else "false"
    elif value_type == "integer":
        try:
            return str(int(value))
        except (ValueError, TypeError):
            return "0"
    return str(value)


def list_settings() -> list[SettingRecord]:
    """Return all setting records."""
    return list(setting_crud.list())


def get_all_settings_raw() -> list[dict[str, Any]]:
    """Fetch a setting by key."""
    return [x.to_dict() for x in list_settings()]


def get_all_settings_ready() -> dict[str, Any]:
    """Fetch all settings parsed into their respective Python types."""
    records: dict[str, Any] = {}

    for x in list_settings():
        val = None
        if x.value_type == "boolean":
            val = x.value == "true"
        elif x.value_type == "integer":
            if isinstance(x.value, int):
                val = x.value
            else:
                try:
                    val = int(x.value)  # type: ignore
                except (ValueError, TypeError):
                    val = None
        elif x.value_type == "string":
            val = str(x.value)

        if val is None:
            logger.warning("Could not parse setting %s with value %s", x.key, x.value)

        records[x.key] = val

    return records


def get_setting_by_key(key: str) -> SettingRecord | None:
    """Fetch a setting by key."""
    return setting_crud.get_by(key=key)


def get_setting_by_id(setting_id: int) -> SettingRecord | None:
    """Get a setting record by ID."""
    orm_obj = setting_crud.get(setting_id)
    if not orm_obj:
        logger.warning(f"Setting record with ID {setting_id} not found")
        return None
    return orm_obj


@db_guard(default_return=False)
def update_setting(
    key: str,
    value: Any,
    value_type: str = "string",
    title: str | None = None,
) -> bool:
    """
    Update an existing setting.
    """
    setting = setting_crud.get_by(key=key)
    if not setting:
        return False

    if not value_type:
        value_type = setting.value_type

    kwargs = {"value": _serialize_value(value, value_type)}
    if title:
        kwargs["title"] = title

    setting_crud.update(setting.id, **kwargs)
    return True


def create_setting(
    key: str,
    title: str,
    value_type: str = "boolean",
    value: Any | None = None,
) -> bool:
    """
    Create new setting.
    """
    key = key.strip()
    title = title.strip()
    if not key:
        raise ValueError("Key is required")
    if not title:
        raise ValueError("Title is required")

    default_value_types = {
        "boolean": "false",
        "integer": "0",
    }

    value = value or default_value_types.get(value_type, "")

    try:
        setting_crud.create(
            key=key,
            title=title,
            value_type=value_type,
            value=str(value) if value is not None else None,
        )
        return True
    except IntegrityError:
        return False
    except Exception:
        return False


__all__ = [
    "list_settings",
    "get_setting_by_id",
    "get_setting_by_key",
    "get_all_settings_raw",
    "update_setting",
    "create_setting",
    "list_settings",
    "get_all_settings_ready",
]
