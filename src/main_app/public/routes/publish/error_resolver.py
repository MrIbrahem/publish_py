"""
ErrorFileResolver : decides which "to_do" file a result belongs to
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Error file resolution
# --------------------------------------------------------------------------- #
class ErrorFileResolver:
    """Maps edit / Wikidata results to the name of the to_do file."""

    MAIN_ERRORS: tuple[str, ...] = (
        "protectedpage",
        "titleblacklist",
        "ratelimited",
        "editconflict",
        "spam filter",
        "abusefilter",
        "mwoauth-invalid-authorization",
    )
    WIKIDATA_ERRORS: dict[str, str] = {
        "Links to user pages": "wd_user_pages",
        "get_csrftoken": "wd_csrftoken",
        "protectedpage": "wd_protectedpage",
    }

    @classmethod
    def resolve(cls, editit: Any, placeholder: str) -> str:
        """Determine the appropriate error file based on error content.

        Args:
            editit: Edit (or link) result
            placeholder: Default file name ("errors" for edits, else Wikidata)
        """
        c_text = json.dumps(editit)

        if placeholder == "errors":
            for err in cls.MAIN_ERRORS:
                if err in c_text:
                    return err
        else:
            for err, file_name in cls.WIKIDATA_ERRORS.items():
                if err in c_text:
                    return file_name

        return placeholder

    @classmethod
    def for_edit(cls, editit: dict[str, Any]) -> str:
        """Pick the to_do file for the result of the edit request."""
        edit = editit.get("edit", {})
        if edit.get("result", "") == "Success":
            return "success"
        if edit.get("captcha"):
            return "captcha"
        return cls.resolve(editit, "errors")


__all__ = [
    "ErrorFileResolver",
]
