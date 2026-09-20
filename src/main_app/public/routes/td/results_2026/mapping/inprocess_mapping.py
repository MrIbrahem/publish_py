""" """

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

from markupsafe import Markup, escape

from ......services.utils.wiki_links import (
    content_translation_url,
)
from .shared_mapping import ItemBase, Stats

logger = logging.getLogger(__name__)


@dataclass
class InProcessItem(ItemBase):
    """One row of the In-process table.

    Port of ``results_2026/results_table_inprocess.php`` — like
    :class:`MissingItem`, the row holds only its own data and the template
    supplies the request context to :meth:`render`.
    """

    user: str
    date: str

    # Request-level config supplied by the table (not available in the template).
    endpoint: str = ""
    translate_type_info: dict[str, int | None] = field(default_factory=dict)

    @classmethod
    def from_row(
        cls,
        *,
        title: str,
        counter: int,
        row: dict[str, Any],
        title_tab: dict[str, Any],
        endpoint: str = "",
        translate_type_info: dict[str, int | None] | None = None,
    ) -> InProcessItem:
        """ """
        translate_type_info = translate_type_info or {"tt_lead": None, "tt_full": None}
        tra_type = title_tab.get("translate_type") or "lead"

        return cls(
            counter=counter,
            title=title or row.get("title") or "",
            en_views=row.get("en_views") or "",
            importance=row.get("importance") or "Unknown",
            qid=row.get("qid") or "",
            user=title_tab.get("user") or "",
            date=title_tab.get("add_date") or title_tab.get("date") or "",
            tra_type=tra_type,
            endpoint=endpoint,
            words=Stats.load(row, "words"),
            refs=Stats.load(row, "refs"),
            translate_type_info=translate_type_info,
        )

    def translate_html(
        self,
        langcode: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
        show_translation_button: bool,
    ) -> Markup:
        if show_translation_button is False:
            return Markup("")

        # logic from results_table.php — anonymous user
        if not is_authenticated:
            return self._login_html()

        effective_type = "all" if self.is_video else (self.tra_type or "lead")
        lead_url = content_translation_url(self.title, langcode, camp, effective_type, self.endpoint)

        if full_tr_user and not self.is_video:
            full_url = content_translation_url(self.title, langcode, camp, "all", self.endpoint)
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

    def _render(
        self,
        langcode: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
        show_translation_button: bool,
    ) -> Markup:
        row_links = self.translate_html(
            langcode,
            camp,
            full_tr_user,
            is_authenticated,
            show_translation_button,
        )
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
            row_links=row_links,
            en_views=self.en_views,
            importance=self.importance,
            words=self.words.all if self.tra_type == "all" else self.words.lead,
            refs=self.refs.all if self.tra_type == "all" else self.refs.lead,
            qid=escape(self.qid),
            user=self.user,
            date=self.date,
        )

    def render(
        self,
        langcode: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
        show_translation_button: bool,
    ) -> Markup:
        no_lead = self.translate_type_info["tt_lead"] == 0
        is_full_eligible = self.translate_type_info["tt_full"] == 1

        return self._render(
            langcode=langcode,
            camp=camp,
            full_tr_user=full_tr_user,
            is_authenticated=is_authenticated,
            show_translation_button=show_translation_button,
        )


__all__ = [
    "InProcessItem",
]
