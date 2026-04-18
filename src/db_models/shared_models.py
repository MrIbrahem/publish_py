from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ..app_main.shared.utils.decode_bytes import coerce_bytes

logger = logging.getLogger(__name__)


@dataclass
class CategoryRecord:
    """
    Category records.
    """

    id: int
    category: str
    campaign: str
    display: str | None = ""
    category2: str | None = ""
    depth: int = 0
    is_default: int = 0

    def to_dict(self) -> dict:
        """Convert the CategoryRecord to a dictionary."""
        return {
            "id": self.id,
            "category": self.category,
            "campaign": self.campaign,
            "display": self.display,
            "category2": self.category2,
            "depth": self.depth,
            "is_default": self.is_default,
        }

    def __post_init__(self) -> None:
        # Validate that required fields are not empty
        if not self.category:
            raise ValueError("Category name cannot be empty")

        if not self.campaign:
            raise ValueError("Campaign name cannot be empty")

        self.depth = int(self.depth) or 0
        self.is_default = int(self.is_default) or 0


@dataclass
class PageRecord:
    """Representation of a page."""

    id: int
    title: str
    word: int | None = None
    translate_type: str | None = None
    cat: str | None = None
    lang: str | None = None
    user: str | None = None
    target: str | None = None
    date: Any | None = None
    pupdate: str | None = None
    add_date: Any | None = None
    deleted: int = 0
    mdwiki_revid: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "word": self.word,
            "translate_type": self.translate_type,
            "cat": self.cat,
            "lang": self.lang,
            "user": self.user,
            "target": self.target,
            "date": self.date,
            "pupdate": self.pupdate,
            "add_date": self.add_date,
            "deleted": self.deleted,
            "mdwiki_revid": self.mdwiki_revid,
        }


@dataclass
class QidRecord:
    """
    QID records.
    add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    """

    id: int
    qid: str
    title: str
    add_date: str

    def to_dict(self) -> dict:
        """Convert the QidRecord to a dictionary."""
        return {
            "id": self.id,
            "qid": self.qid,
            "title": self.title,
            "add_date": self.add_date,
        }

    def __post_init__(self) -> None:
        # Validate that required fields are not empty
        if not self.title:
            raise ValueError("Title cannot be empty")

        if not self.qid:
            raise ValueError("QID cannot be empty")

        # Validate QID format (should start with Q followed by digits)
        if not self.qid.startswith("Q") or not self.qid[1:].isdigit():
            raise ValueError(f"Invalid QID format: {self.qid}. QID should start with 'Q' followed by digits.")


@dataclass
class ReportRecord:
    """Representation of a report record."""

    id: int
    date: Any
    title: str
    user: str
    lang: str
    sourcetitle: str
    result: str
    data: str

    def to_dict(self) -> dict[str, Any]:
        """Convert a ReportRecord to a dictionary."""
        # Handle date conversion with None safety
        if self.date is None:
            date_str = ""
        elif hasattr(self.date, "isoformat"):
            date_str = self.date.isoformat()
        else:
            date_str = str(self.date)

        return {
            "id": self.id,
            "date": date_str,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "sourcetitle": self.sourcetitle,
            "result": self.result,
            "data": self.data,
        }


@dataclass
class UserPageRecord:
    """Representation of a page."""

    id: int
    title: str
    word: int | None = None
    translate_type: str | None = None
    cat: str | None = None
    lang: str | None = None
    user: str | None = None
    target: str | None = None
    date: Any | None = None
    pupdate: str | None = None
    add_date: Any | None = None
    deleted: int = 0
    mdwiki_revid: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "word": self.word,
            "translate_type": self.translate_type,
            "cat": self.cat,
            "lang": self.lang,
            "user": self.user,
            "target": self.target,
            "date": self.date,
            "pupdate": self.pupdate,
            "add_date": self.add_date,
            "deleted": self.deleted,
            "mdwiki_revid": self.mdwiki_revid,
        }


@dataclass
class UserTokenRecord:
    """Decrypted OAuth credential bundle stored in the database."""

    user_id: int
    username: str
    access_token: bytes
    access_secret: bytes
    created_at: Any | None = None
    updated_at: Any | None = None
    last_used_at: Any | None = None
    rotated_at: Any | None = None

    def decrypted(self) -> tuple[str, str]:
        """Return the decrypted access token and secret."""
        from ..app_main.shared.core.crypto import decrypt_value

        access_key = decrypt_value(self.access_token)
        access_secret = decrypt_value(self.access_secret)
        return access_key, access_secret

    def __post_init__(self) -> None:
        self.access_token = coerce_bytes(self.access_token)
        self.access_secret = coerce_bytes(self.access_secret)


__all__ = [
    "PageRecord",
    "ReportRecord",
    "UserTokenRecord",
    "CategoryRecord",
    "UserPageRecord",
    "QidRecord",
]
