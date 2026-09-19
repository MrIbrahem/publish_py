""" """

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal
from urllib.parse import quote

from markupsafe import Markup, escape

from ......services.utils.wiki_links import (
    content_translation_url,
    wikipedia_link,
)
from ._common import _login_html

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


__all__ = [
    "ExistsItem",
]
