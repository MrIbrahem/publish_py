"""Row mapping items for results tables."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal

from flask import url_for
from markupsafe import Markup, escape

from ......services.utils.wiki_links import (
    content_translation_url,
    tr_link_medwiki,
    wikidata_link,
    wikipedia_link,
)

logger = logging.getLogger(__name__)


@dataclass
class Stats:
    lead: int
    all: int

    @classmethod
    def from_row(cls, row: dict[str, Any], stat_type: Literal["words", "refs"]) -> Stats:
        if stat_type == "words":
            return cls(lead=row.get("w_lead_words") or 0, all=row.get("w_all_words") or 0)
        else:
            return cls(lead=row.get("r_lead_refs") or 0, all=row.get("r_all_refs") or 0)


@dataclass
class BaseItem:
    counter: int
    title: str
    qid: str

    @property
    def display_title(self) -> str:
        """User-visible article title with underscores replaced by spaces."""
        return self.title.replace("_", " ")

    @property
    def encoded_title(self) -> str:
        """Escaped Wiki title for URL construction."""
        return escape(self.title.replace(" ", "_"))

    @property
    def is_video(self) -> bool:
        """Check if article is a video title (PHP ``str_starts_with(strtolower($title), "video:")``)."""
        return self.title.lower().startswith("video:")

    def _get_login_html(self) -> Markup:
        """Default unauthenticated login button HTML."""
        login_url = url_for("auth.login")
        return Markup(
            "<a class='btn btn-outline-primary' href='{login_url}'>"
            "<i class='bi bi-box-arrow-in-right'></i> <span class='navtitles'>Login</span>"
            "</a>"
        ).format(login_url=login_url)

    def translate_html(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
    ) -> Markup:
        """Generate translation column HTML based on authentication state."""
        if not is_authenticated:
            return self._get_login_html()

        return self._build_translate_html(langcode, cat, camp, full_tr_user)

    def _build_translate_html(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
    ) -> Markup:
        """Subclass hook to generate translation links for authenticated users."""
        return Markup("")


@dataclass
class MissingItem(BaseItem):
    words: Stats
    refs: Stats
    en_views: str
    importance: str
    tra_type: str
    is_full_row: bool
    translate_type_info: dict[str, int | None] = field(default_factory=dict)

    @property
    def n(self) -> str:
        # PHP "$count = $full && (substr != 'video:') ? '$count.Full' : $count"
        return f"{self.counter}.Full" if self.is_full_row and not self.is_video else str(self.counter)

    @classmethod
    def from_row(
        cls,
        title: str,
        counter: int,
        row: dict[str, Any],
        tra_type: str,
        is_full_row: bool,
        translate_type_info: dict[str, int | None] | None = None,
    ) -> MissingItem:
        translate_type_info = translate_type_info or {"tt_lead": None, "tt_full": None}
        return cls(
            counter=counter,
            title=title or row.get("title") or "",
            qid=row.get("qid") or "",
            words=Stats.from_row(row, "words"),
            refs=Stats.from_row(row, "refs"),
            en_views=row.get("en_views") or "",
            importance=row.get("importance") or "Unknown",
            tra_type=tra_type,
            is_full_row=is_full_row,
            translate_type_info=translate_type_info,
        )

    def _get_login_html(self) -> Markup:
        login_url = url_for("auth.login")
        return Markup("<a href='{login_url}' class='btn btn-outline-primary btn-sm'>Login</a>").format(
            login_url=login_url
        )

    def _build_translate_html(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
    ) -> Markup:
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

    def render(
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
            encoded_title=self.encoded_title,
            title=self.title,
            row_links=row_links,
            en_views=self.en_views,
            importance=self.importance,
            words=self.words.all if self.tra_type == "all" else self.words.lead,
            refs=self.refs.all if self.tra_type == "all" else self.refs.lead,
            qid=self.qid,
        )


@dataclass
class ExistsItem(BaseItem):
    target: str
    via: str
    user_coord: bool
    endpoint: str

    @classmethod
    def from_row(
        cls,
        *,
        title: str,
        counter: int,
        target_tab: dict[str, Any],
        user_coord: bool,
        endpoint: str,
    ) -> ExistsItem:
        title = title.replace("_", " ")
        return cls(
            counter=counter,
            title=title,
            qid=target_tab.get("qid") or "",
            target=target_tab.get("target") or "",
            via=target_tab.get("via") or "",
            user_coord=user_coord,
            endpoint=endpoint,
        )

    def _build_translate_html(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
    ) -> Markup:
        if self.user_coord:
            translate_url = content_translation_url(self.display_title, langcode, camp, "lead", self.endpoint)
            return Markup(
                "<div class='inline'>"
                "<a href='{translate_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
                "</div>"
            ).format(translate_url=translate_url)
        return Markup("")

    def render(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
    ) -> Markup:
        row_links = self.translate_html(langcode, cat, camp, full_tr_user, is_authenticated)
        translated_html = wikipedia_link(self.target, langcode) if (self.target and self.via == "td") else ""
        translated_before_html = wikipedia_link(self.target, langcode) if (self.target and self.via != "td") else ""
        qid_html = wikidata_link(self.qid)

        return Markup("""
            <tr>
                <th scope="row" style="text-align: center">{counter}</th>
                <td class="link_container spannowrap">
                    <a href="https://mdwiki.org/wiki/{encoded_title}" target="_blank">
                        {display_title}
                    </a>
                </td>
                <th>
                    {row_links}
                </th>
                <td>
                    {translated_html}
                </td>
                <td>
                    {translated_before_html}
                </td>
                <td>
                    {qid_html}
                </td>
            </tr>
        """).format(
            counter=self.counter,
            encoded_title=self.encoded_title,
            display_title=self.display_title,
            row_links=row_links,
            translated_html=Markup(translated_html),
            translated_before_html=Markup(translated_before_html),
            qid_html=Markup(qid_html),
        )


@dataclass
class InProcessItem(BaseItem):
    words: Stats
    refs: Stats
    importance: str
    en_views: str
    tra_type: str
    user: str
    date: str
    inprocess_button: str
    endpoint: str
    is_full_row: bool = False

    @classmethod
    def from_row(
        cls,
        *,
        title: str,
        counter: int,
        title_tab: dict[str, Any],
        title_data: dict[str, Any],
        inprocess_button: str,
        endpoint: str,
    ) -> InProcessItem:
        from ._common import _is_video, _row_metrics
        from .in_process_row_builder import _format_inprocess_date

        tra_type = title_tab.get("translate_type") or "lead"
        if _is_video(title):
            tra_type = "all"

        words, refs, importance, en_views, qid = _row_metrics(title_data, tra_type)
        user = title_tab.get("user") or ""
        date_str = _format_inprocess_date(title_tab.get("add_date") or title_tab.get("date"))

        return cls(
            counter=counter,
            title=title,
            qid=qid,
            words=Stats.from_row(title_data, "words"),
            refs=Stats.from_row(title_data, "refs"),
            importance=importance,
            en_views=en_views,
            tra_type=tra_type,
            user=user,
            date=date_str,
            inprocess_button=inprocess_button,
            endpoint=endpoint,
            is_full_row=False,
        )

    def _build_translate_html(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
    ) -> Markup:
        if self.inprocess_button != "1":
            return Markup("")

        effective_type = "all" if self.is_video else (self.tra_type or "lead")
        full_url = content_translation_url(self.title, langcode, camp, "all", self.endpoint)
        lead_url = content_translation_url(self.title, langcode, camp, effective_type, self.endpoint)

        if full_tr_user and not self.is_video:
            return Markup(
                "<div class='inline'>"
                "<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Lead</a>"
                "<a href='{full_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Full</a>"
                "</div>"
            ).format(lead_url=lead_url, full_url=full_url)

        return Markup(
            "<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
        ).format(lead_url=lead_url)

    def render(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
    ) -> Markup:
        row_links = self.translate_html(langcode, cat, camp, full_tr_user, is_authenticated)
        qid_html = wikidata_link(self.qid)

        return Markup("""
            <tr>
                <th class="num" scope="row">{counter}</th>
                <td class="link_container">
                    <a target="_blank" href="https://mdwiki.org/wiki/{encoded_title}">
                        {title}
                    </a>
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
                    {qid_html}
                </td>
                <td>
                    {user}
                </td>
                <td>
                    {date}
                </td>
            </tr>
        """).format(
            counter=self.counter,
            encoded_title=self.encoded_title,
            title=self.title,
            row_links=row_links,
            en_views=self.en_views,
            importance=self.importance,
            words=self.words.all if self.tra_type == "all" else self.words.lead,
            refs=self.refs.all if self.tra_type == "all" else self.refs.lead,
            qid_html=Markup(qid_html),
            user=self.user,
            date=self.date,
        )


__all__ = [
    "BaseItem",
    "MissingItem",
    "ExistsItem",
    "InProcessItem",
]
