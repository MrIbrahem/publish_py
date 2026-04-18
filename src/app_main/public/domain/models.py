"""
Public domain models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AssessmentRecord:
    """Representation of an assessment record."""

    id: int
    title: str
    importance: str | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "importance": self.importance,
        }


@dataclass
class EnwikiPageviewRecord:
    """Representation of an enwiki pageview record."""

    id: int
    title: str
    en_views: int | None = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "en_views": self.en_views,
        }


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
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "user": self.user,
            "lang": self.lang,
            "cat": self.cat,
            "translate_type": self.translate_type,
            "word": self.word,
            "add_date": self.add_date,
        }


@dataclass
class LangRecord:
    """Representation of a language record."""

    lang_id: int
    code: str
    autonym: str
    name: str

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
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
        """Convert record to dictionary."""
        return {
            "title": self.title,
            "revid": self.revid,
        }


@dataclass
class PagesUsersToMainRecord:
    """Representation of a pages_users_to_main record."""

    id: int
    new_target: str = ""
    new_user: str = ""
    new_qid: str = ""

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "new_target": self.new_target,
            "new_user": self.new_user,
            "new_qid": self.new_qid,
        }


@dataclass
class ProjectRecord:
    """Representation of a project record."""

    g_id: int
    g_title: str

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "g_id": self.g_id,
            "g_title": self.g_title,
        }


@dataclass
class RefsCountRecord:
    """Representation of a refs_counts record."""

    r_id: int
    r_title: str
    r_lead_refs: int | None = None
    r_all_refs: int | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "r_id": self.r_id,
            "r_title": self.r_title,
            "r_lead_refs": self.r_lead_refs,
            "r_all_refs": self.r_all_refs,
        }


@dataclass
class TranslateTypeRecord:
    """Representation of a translate_type record."""

    tt_id: int
    tt_title: str
    tt_lead: int = 1
    tt_full: int = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "tt_id": self.tt_id,
            "tt_title": self.tt_title,
            "tt_lead": self.tt_lead,
            "tt_full": self.tt_full,
        }


@dataclass
class UserRecord:
    """Representation of a user record."""

    user_id: int
    username: str
    email: str = ""
    wiki: str = ""
    user_group: str = "Uncategorized"
    reg_date: Any | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "wiki": self.wiki,
            "user_group": self.user_group,
            "reg_date": self.reg_date,
        }


@dataclass
class ViewsNewRecord:
    """Representation of a views_new record."""

    id: int
    target: str
    lang: str
    year: int
    views: int | None = 0

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "target": self.target,
            "lang": self.lang,
            "year": self.year,
            "views": self.views,
        }


@dataclass
class WordRecord:
    """Representation of a words record."""

    w_id: int
    w_title: str
    w_lead_words: int | None = None
    w_all_words: int | None = None

    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "w_id": self.w_id,
            "w_title": self.w_title,
            "w_lead_words": self.w_lead_words,
            "w_all_words": self.w_all_words,
        }


__all__ = [
    "AssessmentRecord",
    "EnwikiPageviewRecord",
    "InProcessRecord",
    "LangRecord",
    "MdwikiRevidRecord",
    "PagesUsersToMainRecord",
    "ProjectRecord",
    "RefsCountRecord",
    "TranslateTypeRecord",
    "UserRecord",
    "ViewsNewRecord",
    "WordRecord",
]
