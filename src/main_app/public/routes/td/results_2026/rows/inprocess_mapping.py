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
from ._common import _format_inprocess_date, _is_video, _row_metrics, _login_html

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
    "InProcessItem",
]
