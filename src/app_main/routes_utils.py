#
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def load_auth_payload(user: Any | None):
    auth_payload: Dict[str, Any] = {}
    if user:
        # returns (access_key, access_secret) and marks token used
        access_key, access_secret = user.access_token, user.access_secret

        # if hasattr(user, "decrypted"): access_key, access_secret = user.decrypted()

        auth_payload = {
            "id": user.user_id,
            "username": user.username,
            "access_token": access_key,
            "access_secret": access_secret,
        }
    return auth_payload


def _format_timestamp(value: datetime | str | None) -> tuple[str, str]:
    """
    Format a timestamp value for user display and provide a sortable ISO-style key.

    Parameters:
        value (datetime | str | None): The timestamp to format. May be a datetime, a string (ISO format or "%Y-%m-%d %H:%M:%S"), or None.

    Returns:
        tuple[str, str]: A pair (display, sort_key).
            - display: human-readable timestamp in "YYYY-MM-DD HH:MM:SS", an empty string if `value` is None, or the original string if it could not be parsed.
            - sort_key: an ISO-format timestamp suitable for sorting, an empty string if `value` is None, or the original string if it could not be parsed.
    """
    if not value:
        return "", ""

    dt = None

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            # First, try parsing as an ISO 8601 format string.
            dt = datetime.fromisoformat(value)
        except (TypeError, ValueError):
            try:
                # If that fails, try the specific "%Y-%m-%d %H:%M:%S" format.
                dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except (TypeError, ValueError):
                # If both fail, dt remains None.
                pass

    if not dt:
        return str(value), str(value)

    display = dt.strftime("%Y-%m-%d %H:%M:%S")
    sort_key = dt.isoformat()

    return display, sort_key
