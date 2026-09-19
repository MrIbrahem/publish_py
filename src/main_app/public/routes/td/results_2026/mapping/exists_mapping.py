""" """

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

from markupsafe import Markup, escape

from ......services.utils.wiki_links import (
    content_translation_url,
    wikipedia_link,
)
from ..rows._common import _login_html
from .shared_mapping import ItemBase, Stats

logger = logging.getLogger(__name__)


@dataclass
class ExistsItem(ItemBase):
    """One row of the Exists (already translated) table.

    Port of ``results_2026/results_table_exists.php`` — the row carries only
    its own data; request-level context (``langcode``/``camp``/auth) is passed
    to :meth:`render` by the template, mirroring :class:`MissingItem`.
    """

    target: str
    via: str
    qid: str

    # Request-level config supplied by the table (not available in the template).
    endpoint: str = ""
    translate_type_info: dict[str, int | None] = field(default_factory=dict)

    @classmethod
    def from_row(
        cls,
        title: str,
        counter: int,
        row: dict[str, Any],
        *,
        endpoint: str = "",
        translate_type_info: dict[str, int | None] | None = None,
    ) -> ExistsItem:
        """ """
        translate_type_info = translate_type_info or {"tt_lead": None, "tt_full": None}
        return cls(
            counter=counter,
            title=(title or "").replace("_", " "),
            target=row.get("target") or "",
            via=row.get("via", ""),
            qid=row.get("qid") or "",
            endpoint=endpoint,
            en_views="",
            importance="",
            tra_type="",
            words=Stats.load(row, "words"),
            refs=Stats.load(row, "refs"),
            translate_type_info=translate_type_info,
        )

    def translate_html(
        self,
        langcode: str,
        camp: str,
        is_authenticated: bool,
        user_coord: bool,
    ) -> Markup:
        """PHP ``make_one_row_exists_2026`` — Translate column."""
        # logic from results_table_exists.php — anonymous user
        if not is_authenticated:
            return _login_html()

        # PHP: the button is rendered only for coordinators ($user_coord).
        if not user_coord:
            return Markup("")

        translate_url = content_translation_url(self.title, langcode, camp, "lead", self.endpoint)
        return Markup(
            "<div class='inline'>"
            "<a href='{translate_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
            "</div>"
        ).format(translate_url=translate_url)

    def _render(
        self,
        langcode: str,
        camp: str,
        is_authenticated: bool,
        user_coord: bool,
    ) -> Markup:
        # PHP: target goes to the "Translated" column when via == 'td',
        # otherwise to the "Translated before" column.
        translated = self.target if (self.target and self.via == "td") else ""
        translated_before = self.target if (self.target and self.via != "td") else ""

        row_links = self.translate_html(langcode, camp, is_authenticated, user_coord)

        return Markup("""
            <tr>
                <th scope="row" style="text-align: center">
                    {counter}
                </th>
                <td class="link_container spannowrap">
                    <a target="_blank" href="https://mdwiki.org/wiki/{encoded_title}">
                        {title}
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
            encoded_title=quote(self.title.replace(" ", "_")),
            title=self.title,
            row_links=row_links,
            translated_html=Markup(wikipedia_link(translated, langcode)),
            translated_before_html=Markup(wikipedia_link(translated_before, langcode)),
            qid=escape(self.qid),
        )

    def render(
        self,
        langcode: str,
        camp: str,
        is_authenticated: bool,
        user_coord: bool,
    ) -> Markup:
        no_lead = self.translate_type_info["tt_lead"] == 0
        is_full_eligible = self.translate_type_info["tt_full"] == 1

        return self._render(
            langcode=langcode,
            camp=camp,
            is_authenticated=is_authenticated,
            user_coord=user_coord,
        )


__all__ = [
    "ExistsItem",
]
