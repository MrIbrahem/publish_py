""" """

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal
from urllib.parse import quote

from flask import url_for
from markupsafe import Markup, escape

from ......services.utils.wiki_links import (
    content_translation_url,
    tr_link_medwiki,
    wikipedia_link,
)
from ._common import _format_inprocess_date, _is_video, _row_metrics

logger = logging.getLogger(__name__)


def _login_html() -> Markup:
    """Login button shown to anonymous users (PHP ``results_table*.php``)."""
    return Markup(
        "<a class='btn btn-outline-primary' href='{login_url}'>"
        "<i class='bi bi-box-arrow-in-right'></i> <span class='navtitles'>Login</span>"
        "</a>"
    ).format(login_url=url_for("auth.login"))


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
            encoded_title=quote(self.title.replace(" ", "_")),
            title=self.title,
            row_links=row_links,
            en_views=self.en_views,
            importance=self.importance,
            words=self.words.all if self.tra_type == "all" else self.words.lead,
            refs=self.refs.all if self.tra_type == "all" else self.refs.lead,
            qid=self.qid,
        )


@dataclass
class ExistsItem:
    """One row of the Exists (already translated) table.

    Port of ``results_2026/results_table_exists.php`` — the row carries only
    its own data; request-level context (``langcode``/``camp``/auth) is passed
    to :meth:`render` by the template, mirroring :class:`MissingItem`.
    """

    counter: int

    display_title: str
    target: str
    via: str
    qid: str

    # Request-level config supplied by the table (not available in the template).
    endpoint: str = ""
    user_coord: bool = False

    @classmethod
    def from_row(
        cls,
        title: str,
        counter: int,
        target_tab: dict,
        *,
        endpoint: str = "",
        user_coord: bool = False,
    ) -> ExistsItem:
        """ """
        return cls(
            counter=counter,
            display_title=(title or "").replace("_", " "),
            target=target_tab.get("target") or "",
            via=target_tab.get("via", ""),
            qid=target_tab.get("qid") or "",
            endpoint=endpoint,
            user_coord=user_coord,
        )

    def translate_html(self, langcode: str, camp: str, is_authenticated: bool) -> Markup:
        """PHP ``make_one_row_exists_2026`` — Translate column."""
        # logic from results_table_exists.php — anonymous user
        if not is_authenticated:
            return _login_html()

        # PHP: the button is rendered only for coordinators ($user_coord).
        if not self.user_coord:
            return Markup("")

        translate_url = content_translation_url(self.display_title, langcode, camp, "lead", self.endpoint)
        return Markup(
            "<div class='inline'>"
            "<a href='{translate_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
            "</div>"
        ).format(translate_url=translate_url)

    def render(self, langcode: str, camp: str, is_authenticated: bool) -> Markup:
        # PHP: target goes to the "Translated" column when via == 'td',
        # otherwise to the "Translated before" column.
        translated = self.target if (self.target and self.via == "td") else ""
        translated_before = self.target if (self.target and self.via != "td") else ""

        return Markup("""
            <tr>
                <th scope="row" style="text-align: center">
                    {counter}
                </th>
                <td class="link_container spannowrap">
                    <a target="_blank" href="https://mdwiki.org/wiki/{encoded_title}">
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
                    <a class='inline' target='_blank' href='https://wikidata.org/wiki/{qid}'>{qid}</a>
                </td>
            </tr>
        """).format(
            counter=self.counter,
            encoded_title=quote(self.display_title.replace(" ", "_")),
            display_title=self.display_title,
            row_links=self.translate_html(langcode, camp, is_authenticated),
            translated_html=Markup(wikipedia_link(translated, langcode)),
            translated_before_html=Markup(wikipedia_link(translated_before, langcode)),
            qid=escape(self.qid),
        )


@dataclass
class InProcessItem:
    """One row of the In-process table.

    Port of ``results_2026/results_table_inprocess.php`` — like
    :class:`MissingItem`, the row holds only its own data and the template
    supplies the request context to :meth:`render`.
    """

    counter: int

    title: str
    en_views: Any
    importance: str
    words: int
    refs: int
    qid: str

    user: str
    date: str

    tra_type: str
    is_video: bool

    # Request-level config supplied by the table (not available in the template).
    endpoint: str = ""
    inprocess_button: str = "0"
    full_tr_user: bool = False

    @classmethod
    def from_row(
        cls,
        *,
        title: str,
        counter: int,
        title_tab: dict[str, Any],
        title_data: dict[str, Any],
        endpoint: str = "",
        inprocess_button: str = "0",
        full_tr_user: bool = False,
    ) -> InProcessItem:
        """ """
        tra_type = title_tab.get("translate_type") or "lead"
        is_video_title = _is_video(title)
        if is_video_title:
            tra_type = "all"

        words, refs, importance, en_views, qid = _row_metrics(title_data, tra_type)

        return cls(
            counter=counter,
            title=title,
            en_views=en_views,
            importance=importance,
            words=words,
            refs=refs,
            qid=qid,
            user=title_tab.get("user") or "",
            date=_format_inprocess_date(title_tab.get("add_date") or title_tab.get("date")),
            tra_type=tra_type,
            is_video=is_video_title,
            endpoint=endpoint,
            inprocess_button=inprocess_button,
            full_tr_user=full_tr_user,
        )

    def translate_html(self, langcode: str, camp: str, is_authenticated: bool) -> Markup:
        """PHP ``make_translate_urls`` — inprocess branch only."""
        # logic from results_table_inprocess.php — anonymous user
        if not is_authenticated:
            return _login_html()

        if self.inprocess_button != "1":
            return Markup("")

        effective_type = "all" if self.is_video else (self.tra_type or "lead")
        full_url = content_translation_url(self.title, langcode, camp, "all", self.endpoint)
        lead_url = content_translation_url(self.title, langcode, camp, effective_type, self.endpoint)

        if self.full_tr_user and not self.is_video:
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
            "<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
        ).format(lead_url=lead_url)

    def render(self, langcode: str, camp: str, is_authenticated: bool) -> Markup:
        return Markup("""
            <tr>
                <th class="num" scope="row">
                    {counter}
                </th>
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
                    <a class='inline' target='_blank' href='https://wikidata.org/wiki/{qid}'>{qid}</a>
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
            encoded_title=quote(self.title.replace(" ", "_")),
            title=self.title,
            row_links=self.translate_html(langcode, camp, is_authenticated),
            en_views=self.en_views,
            importance=self.importance,
            words=self.words,
            refs=self.refs,
            qid=escape(self.qid),
            user=self.user,
            date=self.date,
        )


__all__ = [
    "MissingItem",
    "ExistsItem",
    "InProcessItem",
]
