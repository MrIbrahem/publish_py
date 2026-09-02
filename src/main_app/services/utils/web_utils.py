""" """

import logging

logger = logging.getLogger(__name__)


def parse_select_fields(select_param: str | None) -> list[str] | None:
    """Parse the select parameter into a list of field names."""
    if not select_param:
        return None
    return [f.strip() for f in select_param.split(",") if f.strip()]


__all__ = [
    "parse_select_fields",
]
