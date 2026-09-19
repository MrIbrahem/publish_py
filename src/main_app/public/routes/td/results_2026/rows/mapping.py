""" """

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Literal
from markupsafe import Markup, escape
from flask import url_for
from ......services.utils.wiki_links import tr_link_medwiki

logger = logging.getLogger(__name__)

@dataclass
class Stats:
    lead: int
    all: int

    @classmethod
    def from_row(cls, row: dict, stat_type: Literal["words", "refs"]) -> Stats:
        if stat_type == "words":
            return cls(lead=row.get("w_lead_words") or 0, all=row.get("w_all_words") or 0)
        else:
            return cls(lead=row.get("r_lead_refs") or 0, all=row.get("r_all_refs") or 0)

@dataclass
class MissingItem:
    counter: int

    words: Stats
    refs: Stats

    title: str
    en_views: str
    importance: str
    tra_type: str
    qid: str
    is_full_row: bool

    def is_video(self) -> bool:
        """PHP ``str_starts_with(strtolower($title), "video:")``."""
        return self.title.lower().startswith("video:")

    @property
    def n(self) -> str:
        # PHP "$count = $full && (substr != 'video:') ? '$count.Full' : $count"
        return f"{self.counter}.Full" if self.is_full_row and not self.is_video else str(self.counter)

    @classmethod
    def from_row(cls, title:str, counter, row: dict, tra_type: str, is_full_row: bool) -> MissingItem:
        """ """
        return cls(
            counter=counter,
            title = title or row.get("title") or "",
            en_views = row.get("en_views") or "",
            importance = row.get("importance") or "Unknown",
            qid = row.get("qid") or "",
            tra_type = tra_type,
            is_full_row=is_full_row,
            words = Stats.from_row(row, "words"),
            refs = Stats.from_row(row, "refs"),
        )

    def translate_html(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
    ) -> Markup:
        # logic from results_table.php — anonymous user
        if not is_authenticated:
            login_url = url_for("auth.login")
            return Markup("<a href='{login_url}' class='btn btn-outline-primary btn-sm'>Login</a>").format(
                login_url=login_url
            )

        full_url = tr_link_medwiki(self.title, langcode, cat, camp, "all", self.words.all)
        lead_url = tr_link_medwiki(self.title, langcode, cat, camp, self.tra_type, self.words.lead)

        if full_tr_user and not self.is_video:
            return Markup("""
                <div class='inline'>
                    <a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Lead</a>
                    <a href='{full_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Full</a>
                </div>
            """
            ).format(
                lead_url=lead_url,
                full_url=full_url,
            )

        return Markup("<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>").format(
            lead_url=lead_url
        )

    def render(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
    ) -> Markup:
        row_links = self.translate_html(langcode, cat, camp, full_tr_user, is_authenticated)
        return Markup(
            """
            <tr>
                <th class="num" scope="row">
                    {n}
                </th>
                <td class="link_container">
                    <a target="_blank" href="https://mdwiki.org/wiki/{encoded_title}">
                        {title}
                    </a> {full_note}
                </td>
                <th>
                    {row_links}
                </th>
                <td class="num" style="text-align: left">
                    {en_views}
                </td>
                <td class="num" style="text-align: left">
                    {importance}
                </td>
                <td class="num" style="text-align: left">
                    {words}
                </td>
                <td class="num" style="text-align: left">
                    {refs}
                </td>
                <td>
                    <a class='inline' target='_blank' href='https://wikidata.org/wiki/{qid}'>{qid}</a>
                </td>
            </tr>
        """
        ).format(
            full_note="(Full text)" if self.is_full_row else "",
            n=self.n,
            encoded_title=escape(self.title),
            title=self.title,
            row_links=row_links,
            en_views=self.en_views,
            importance=self.importance,
            words=self.words.all if self.tra_type == "all" else self.words.lead,
            refs=self.refs.all if self.tra_type == "all" else self.refs.lead,
            qid=self.qid,
        )

__all__ = [
    "MissingItem",
]
