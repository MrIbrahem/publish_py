""" """

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import quote

from flask import url_for
from markupsafe import Markup

from ......services.utils.wiki_links import (
    tr_link_medwiki,
)

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
    translate_type_info: dict[str, int | None] = field(default_factory=dict)

    @property
    def is_video(self) -> bool:
        """PHP ``str_starts_with(strtolower($title), "video:")``."""
        return self.title.lower().startswith("video:")

    @property
    def n(self) -> str:
        # PHP "$count = $full && (substr != 'video:') ? '$count.Full' : $count"
        return f"{self.counter}.Full" if self.is_full_row and not self.is_video else str(self.counter)

    @classmethod
    def from_row(
        cls,
        title: str,
        counter,
        row: dict,
        tra_type: str,
        is_full_row: bool,
        translate_type_info: dict[str, int | None] | None = None,
    ) -> MissingItem:
        """ """
        translate_type_info = translate_type_info or {"tt_lead": None, "tt_full": None}
        return cls(
            counter=counter,
            title=title or row.get("title") or "",
            en_views=row.get("en_views") or "",
            importance=row.get("importance") or "Unknown",
            qid=row.get("qid") or "",
            tra_type=tra_type,
            is_full_row=is_full_row,
            words=Stats.from_row(row, "words"),
            refs=Stats.from_row(row, "refs"),
            translate_type_info=translate_type_info,
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

        lead_url = tr_link_medwiki(self.title, langcode, cat, camp, self.tra_type, self.words.lead)

        if full_tr_user and not self.is_video:
            full_url = tr_link_medwiki(self.title, langcode, cat, camp, "all", self.words.all)
            return Markup(
                "<div class='inline'>"
                "<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Lead</a>"
                "<a href='{full_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Full</a>"
                "</div>"
            ).format(
                lead_url=lead_url,
                full_url=full_url,
            )

        return Markup(
            "<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank' title='{tra_type}'>"
            "Translate"
            "</a>"
        ).format(
            lead_url=lead_url,
            tra_type=self.tra_type,
        )

    def _render(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
    ) -> Markup:
        row_links = self.translate_html(langcode, cat, camp, full_tr_user, is_authenticated)
        return Markup("""
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
        """).format(
            full_note="(Full text)" if (self.is_full_row and not self.is_video) else "",
            n=self.counter,
            encoded_title=quote(self.title.replace(" ", "_")),
            title=self.title,
            row_links=row_links,
            en_views=self.en_views,
            importance=self.importance,
            words=self.words.all if self.tra_type == "all" else self.words.lead,
            refs=self.refs.all if self.tra_type == "all" else self.refs.lead,
            qid=self.qid,
        )

    def render(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
    ) -> Markup:
        no_lead = self.translate_type_info["tt_lead"] == 0
        is_full_eligible = self.translate_type_info["tt_full"] == 1

        return self._render(
            langcode=langcode,
            cat=cat,
            camp=camp,
            full_tr_user=full_tr_user,
            is_authenticated=is_authenticated,
        )


__all__ = [
    "MissingItem",
]
