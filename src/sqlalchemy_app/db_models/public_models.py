"""
Public domain models - Dataclasses.

Note: Several models have been moved to specialized modules:
- pages_models.py: PagesUsersToMainRecord
- views_models.py: EnwikiPageviewRecord, ViewsNewRecord, ViewsNewAllRecord
- metrics_models.py: AssessmentRecord, RefsCountRecord, WordRecord
- qid_models.py: QidRecord
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class InProcessRecord:
    """Representation of an in_process record."""

    id: int
    title: str
    user: str
    lang: str
    cat: str | None = "RTT"
    translate_type: str | None = "lead"
    word: int | None = 0
    add_date: Any | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "cat": self.cat,
            "translate_type": self.translate_type,
            "word": self.word,
            "add_date": str(self.add_date) if self.add_date else self.add_date,
        }


@dataclass
class LangRecord:
    """Representation of a language record."""

    lang_id: int
    code: str
    autonym: str
    name: str

    def to_dict(self) -> dict:
        return {
            "lang_id": self.lang_id,
            "code": self.code,
            "autonym": self.autonym,
            "name": self.name,
        }


@dataclass
class MdwikiRevidRecord:
    """Representation of an mdwiki_revids record."""

    title: str
    revid: int

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "revid": self.revid,
        }


@dataclass
class ProjectRecord:
    """Representation of a project record."""

    g_id: int
    g_title: str

    def to_dict(self) -> dict:
        return {
            "g_id": self.g_id,
            "g_title": self.g_title,
        }


@dataclass
class TranslateTypeRecord:
    """Representation of a translate_type record."""

    tt_id: int
    tt_title: str
    tt_lead: int = 1
    tt_full: int = 0

    def to_dict(self) -> dict:
        return {
            "tt_id": self.tt_id,
            "tt_title": self.tt_title,
            "tt_lead": self.tt_lead,
            "tt_full": self.tt_full,
        }


__all__ = [
    "InProcessRecord",
    "LangRecord",
    "MdwikiRevidRecord",
    "ProjectRecord",
    "TranslateTypeRecord",
]
