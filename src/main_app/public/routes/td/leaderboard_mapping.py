""" """

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import quote

from flask import url_for
from markupsafe import Markup

from ....services.utils.views_links import (
    build_pageviews_url,
    build_toget_api_url,
)
from ....services.utils.wiki_links import content_translation_url

logger = logging.getLogger(__name__)


@dataclass
class BaseRow:
    title: str
    lang: str
    user: str | None
    campaign: str | None

    def wiki_link(self, target: str | None = None, deleted: bool = False) -> str:
        if not target or not self.lang:
            return ""

        link = f"""<a href="https://{self.lang}.wikipedia.org/wiki/{quote(target)}" target="_blank">{target}</a>"""
        if deleted:
            link += ' <span class="text-danger">(DELETED)</span>'

        return link

    def mdwiki_link(self) -> str:
        if self.title:
            return f"""<a href="https://mdwiki.org/wiki/{quote(self.title.replace(" ", "_"))}" target="_blank"> {self.title} </a>"""
        return ""

    def wikidata_link(self, qid: str | None) -> str:
        if qid:
            return f"""<a class='inline' target='_blank' href='https://wikidata.org/wiki/{qid}'>{qid}</a>"""
        return ""

    def user_link(self) -> str:
        if self.user:
            url = url_for("leaderboard.users", username=self.user)
            return f"<a href='{url}'> {self.user} </a>"
        return ""

    def lang_link(self) -> str:
        if self.lang:
            url = url_for("leaderboard.langs", lang_code=self.lang)
            return f"<a href='{url}'> {self.lang} </a>"
        return ""

    def campaign_link(self) -> str:
        if self.campaign:
            url = url_for("leaderboard.index", camp=self.campaign)
            return f"""<a href="{url}"> {self.campaign} </a>"""
        return ""

    def translate_row(self, translate_type: str) -> str:
        lead_url = content_translation_url(self.title, self.lang, self.campaign, translate_type)
        return f"""
            <td>
                <a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Complete</a>
            </td>
        """

    @staticmethod
    def _format_inprocess_date(value: Any) -> str:
        """Mirror of PHP ``if (strpos($_date_, ':') !== false) explode(' ', $_date_)[0]``."""
        if value is None:
            return ""
        if hasattr(value, "isoformat"):
            # datetime → ISO; PHP receives "YYYY-MM-DD HH:MM:SS".
            try:
                text = value.isoformat(sep=" ")
            except ValueError:
                text = value.isoformat()
        else:
            text = str(value)
        if ":" in text:
            return text.split(" ", 1)[0]
        return text


@dataclass
class ReadyRow(BaseRow):
    """ """

    word: int | None
    views: int | None
    translate_type: str
    lang: str
    cat: str | None = "RTT"

    deleted: bool = False

    target: str | None = ""
    date: str | None = ""
    pupdate: str | None = ""
    add_date: str | None = ""

    def views_link(self) -> str:
        if not self.target:
            return ""

        # Generate the base Pageviews URL
        url: str = build_pageviews_url(self.lang, self.target, self.pupdate)

        if self.views:
            try:
                str_views = f"{int(self.views):,}"
            except ValueError:
                logger.error("ValueError: %s", type(self.views))  # <class 'decimal.Decimal'>
                str_views = str(self.views)

            # Format views with commas (equivalent to views | commas)
            return f'<a href="{url}" target="_blank">{str_views}</a>'

        # Generate the API URL for 'toget'
        url2: str = build_toget_api_url(self.lang, self.target, self.pupdate)
        return f'<a target="_blank" name="toget" data-json-url="{url2}" href="{url}">?</a>'

    @classmethod
    def from_row(
        cls,
        row: dict[str, Any],
    ) -> ReadyRow:
        """ """
        return cls(
            title=row.get("title") or "",
            word=row.get("word") or 0,
            views=row.get("views") or 0,
            translate_type=row.get("translate_type") or "",
            user=row.get("user") or "",
            lang=row.get("lang") or "",
            target=row.get("target") or "",
            cat=row.get("cat") or "",
            deleted=bool(row.get("deleted")) or False,
            campaign=row.get("campaign") or "",
            add_date=cls._format_inprocess_date(row.get("add_date") or ""),
            pupdate=cls._format_inprocess_date(row.get("pupdate") or ""),
            # date=cls._format_inprocess_date(row.get("date") or ""),
            date=row.get("date") or "",
        )

    def render(
        self,
        index: int,
        lang_or_user_row: Literal["user", "lang"],
        show_translate_type_row: bool = False,
    ) -> Markup:
        lang_user_link = self.lang_link() if lang_or_user_row == "lang" else self.user_link()
        campaign_link = self.campaign_link()
        target_link = self.wiki_link(self.target, self.deleted)
        views_link = self.views_link()
        mdwiki_link = self.mdwiki_link()
        translate_type_row = ""
        if show_translate_type_row:
            translate_type_row = f"<td> {self.translate_type} </td>"
        return Markup("""
            <tr>
                <th> {index} </th>
                <td> {lang_user_link} </td>
                <td> {mdwiki_link} </td>
                <td> {campaign_link} </td>
                {translate_type_row}
                <td> {word} </td>
                <td> {target_link} </td>
                <td> {pupdate} </td>
                <td> {views_link} </td>
            </tr>
        """).format(
            index=index,
            mdwiki_link=Markup(mdwiki_link),
            lang_user_link=Markup(lang_user_link),
            campaign_link=Markup(campaign_link),
            translate_type_row=Markup(translate_type_row),
            word=self.word,
            pupdate=self.pupdate,
            views_link=Markup(views_link),
            target_link=Markup(target_link),
        )


@dataclass
class InProcessRow(BaseRow):
    """ """

    lang: str
    translate_type: str
    word: int | None
    add_date: str
    cat: str | None = "RTT"

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
            add_date=row.get("add_date") or "",
        )

    def render(
        self,
        index: int,
        lang_or_user_row: Literal["user", "lang"],
        show_translate_row: bool = False,
    ) -> Markup:
        lang_user_link = self.lang_link() if lang_or_user_row == "lang" else self.user_link()
        campaign_link = self.campaign_link()
        mdwiki_link = self.mdwiki_link()
        translate_row = self.translate_row(self.translate_type) if show_translate_row else ""

        return Markup("""
            <tr>
                <th> {index} </th>
                <td> {lang_user_link} </td>
                <td> {mdwiki_link} </td>
                <td> {campaign_link} </td>
                <td> {translate_type} </td>
                <td> {word} </td>
                <td> Pending </td>
                <td> {add_date} </td>
                {translate_row}
            </tr>
        """).format(
            index=index,
            mdwiki_link=Markup(mdwiki_link),
            lang_user_link=Markup(lang_user_link),
            campaign_link=Markup(campaign_link),
            translate_type=self.translate_type,
            word=self.word,
            add_date=self.add_date,
            translate_row=Markup(translate_row),
        )


__all__ = [
    "ReadyRow",
    "InProcessRow",
]
