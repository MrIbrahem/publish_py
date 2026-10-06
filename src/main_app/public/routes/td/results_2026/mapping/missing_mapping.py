""" """

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import quote

from markupsafe import Markup

from ......services.utils.wiki_links import tr_link_medwiki
from .shared_mapping import ItemBase, Stats

logger = logging.getLogger(__name__)


@dataclass
class MissingItem(ItemBase):
    is_full_row: bool

    @property
    def n(self) -> str:
        # PHP "$count = $full && (substr != 'video:') ? '$count.Full' : $count"
        return f"{self.counter}.Full" if self.is_full_row and not self.is_video else str(self.counter)

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
            return self._login_html()

        full_url = tr_link_medwiki(self.title, langcode, cat, camp, "all")

        html_translate_button = (
            "<a href='{translate_url}' class='btn btn-outline-primary btn-sm' target='_blank' title='{tra_type}'>"
            "Translate"
            "</a>"
        )
        # 1. if its video, render `full_url` only. no mater if full_tr_user or not
        if self.is_video:
            return Markup(html_translate_button).format(translate_url=full_url, tra_type='all')

        lead_url = tr_link_medwiki(self.title, langcode, cat, camp, self.tra_type)

        # 2. if not `full_tr_user`, render only lead url
        if not full_tr_user:
            return Markup(html_translate_button).format(translate_url=lead_url, tra_type=self.tra_type)

        # 3. if full_tr_user, render both lead and full urls
        return Markup(
            "<div class='inline'>"
            "<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Lead</a>"
            "<a href='{full_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Full</a>"
            "</div>"
        ).format( lead_url=lead_url, full_url=full_url )


    def _render(
        self,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
    ) -> Markup:
        row_links = self.translate_html(
            langcode,
            cat,
            camp,
            full_tr_user,
            is_authenticated,
        )
        return Markup("""
            <tr>
                <th class="num" scope="row"> {counter} </th>
                <td class="link_container"> {mdwiki_link} {full_note} </td>
                <td> {row_links} </td>
                <td class="num" style="text-align: left"> {en_views} </td>
                <td class="num" style="text-align: left"> {importance} </td>
                <td class="num" style="text-align: left"> {words} </td>
                <td class="num" style="text-align: left"> {refs} </td>
                <td> {wikidata_link} </td>
            </tr>
        """).format(
            counter=self.n,
            full_note="(Full text)" if (self.is_full_row and not self.is_video) else "",
            encoded_title=quote(self.title.replace(" ", "_")),
            title=self.title,
            row_links=row_links,
            en_views=self.en_views,
            importance=self.importance,

            words=self.pick_stat_value(self.words),
            refs=self.pick_stat_value(self.refs),

            wikidata_link=Markup(self.wikidata_link()),
            mdwiki_link=Markup(self.mdwiki_link()),
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

    def translate_url(self, lang: str, cat: str, camp: str) -> str:
        return tr_link_medwiki(
            title=self.title,
            langcode=lang,
            cat=cat,
            camp=camp,
            tra_type=self.tra_type,
        )

    # -------------------------------------
    # Factory
    # -------------------------------------
    @classmethod
    def from_row(
        cls,
        title: str,
        counter: int,
        row: dict,
        tra_type: str,
        is_full_row: bool = False,
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
            words=Stats.load(row, "words"),
            refs=Stats.load(row, "refs"),
            translate_type_info=translate_type_info,
        )



__all__ = [
    "MissingItem",
]
