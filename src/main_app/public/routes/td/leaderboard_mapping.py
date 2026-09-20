""" """

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal

from flask import url_for
from markupsafe import Markup

from ....services.utils.wiki_links import (
    content_translation_url,
)
from .results_2026.rows._common import _format_inprocess_date

logger = logging.getLogger(__name__)


@dataclass
class InProcessRow:
    """ """

    title: str
    user: str
    lang: str
    translate_type: str
    word: int | None
    add_date: str
    cat: str | None = "RTT"
    campaign: str | None = ""

    @classmethod
    def from_row(
        cls,
        row: dict[str, Any],
    ) -> InProcessRow:
        """ """
        return cls(
            title=row.get("title") or "",
            user=row.get("user") or "",
            campaign=row.get("campaign") or "",
            lang=row.get("lang") or "",
            translate_type=row.get("translate_type") or "",
            word=row.get("word") or 0,
            add_date=_format_inprocess_date(row.get("add_date")),
        )

    def render(
        self,
        index: int,
        lang_or_user_row: Literal["user", "lang"],
        show_translate_row: bool = False,
    ) -> Markup:
        lang_user_link = ""

        if lang_or_user_row == "lang" and self.lang:
            url = url_for("leaderboard.langs", lang_code=self.lang)
            lang_user_link = f"<a href='{url}'> {self.lang} </a>"

        if lang_or_user_row == "user" and self.user:
            url = url_for("leaderboard.users", username=self.user)
            lang_user_link = f"<a href='{url}'> {self.user} </a>"

        campaign_link = ""
        if self.campaign:
            url = url_for("leaderboard.index", camp=self.campaign)
            campaign_link = f"""<a href="{url}"> {self.campaign} </a>"""

        translate_row = ""
        if show_translate_row:
            lead_url = content_translation_url(self.title, self.lang, self.campaign, self.translate_type)

            translate_row = f"""
            <td>
                <a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Complete</a>
            </td>
            """

        return Markup("""
            <tr>
                <th> {index} </th>
                <th> {lang_user_link} </th>
                <td>
                    <a href="https://mdwiki.org/wiki/{title}" target="_blank">
                        {title}
                    </a>
                </td>
                <th> {campaign_link} </th>
                <td>
                    {translate_type}
                </td>
                <td> {word} </td>
                <td> Pending </td>
                <td> {add_date} </td>
                {translate_row}
            </tr>
        """).format(
            index=index,
            title=self.title,
            lang_user_link=Markup(lang_user_link),
            campaign_link=Markup(campaign_link),
            translate_type=self.translate_type,
            word=self.word,
            add_date=self.add_date,
            translate_row=Markup(translate_row),
        )


__all__ = [
    "InProcessRow",
]
