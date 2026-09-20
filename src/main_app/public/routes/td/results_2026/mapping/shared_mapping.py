""" """

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import quote

from flask import url_for
from markupsafe import Markup

logger = logging.getLogger(__name__)


@dataclass
class Stats:
    lead: int
    all: int

    @classmethod
    def load(cls, row: dict, stat_type: Literal["words", "refs"]) -> Stats:
        if stat_type == "words":
            return cls(lead=row.get("w_lead_words") or 0, all=row.get("w_all_words") or 0)
        else:
            return cls(lead=row.get("r_lead_refs") or 0, all=row.get("r_all_refs") or 0)


@dataclass
class ItemBase:
    counter: int

    words: Stats
    refs: Stats

    title: str
    en_views: str
    importance: str
    tra_type: str
    qid: str

    @property
    def is_video(self) -> bool:
        """PHP ``str_starts_with(strtolower($title), "video:")``."""
        return self.title.lower().startswith("video:")

    def _login_html(self) -> Markup:
        """Login button shown to anonymous users (PHP ``results_table*.php``)."""
        return Markup(
            "<a class='btn btn-outline-primary' href='{login_url}'>"
            "<i class='bi bi-box-arrow-in-right'></i> <span class='navtitles'>Login</span>"
            "</a>"
        ).format(login_url=url_for("auth.login"))

    def mdwiki_link(self) -> str:
        if self.title:
            return f"""<a href="https://mdwiki.org/wiki/{quote(self.title.replace(" ", "_"))}" target="_blank"> {self.title} </a>"""
        return ""

    def wikidata_link(self) -> str:
        if self.qid:
            return f"""<a class='inline' target='_blank' href='https://wikidata.org/wiki/{self.qid}'>{self.qid}</a>"""
        return ""

    @staticmethod
    def _format_inprocess_date(value: Any) -> str:
        """Mirror of PHP ``if (strpos($_date_, ':') !== false) explode(' ', $_date_)[0]``."""
        if value is None:
            return ""
        if hasattr(value, "isoformat"):
            # datetime → ISO; PHP receives "YYYY-MM-DD HH:MM:SS".
            text = value.isoformat(sep=" ")
        else:
            text = str(value)
        if ":" in text:
            return text.split(" ", 1)[0]
        return text


__all__ = [
    "ItemBase",
]
