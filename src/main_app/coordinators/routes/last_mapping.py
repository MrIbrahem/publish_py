""" """

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from flask import url_for
from markupsafe import Markup

from ...services.core.jinja_filters import FormatTimestamps
from ...services.utils.views_links import ViewsLinks

logger = logging.getLogger(__name__)


def _wiki_title(title: str) -> str:
    """Same as the Jinja chain: replace(' ', '_') | urlencode"""
    return quote((title or "").replace(" ", "_"), safe="/")


def safe_int(value: str | int | None, default: int = 0) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


@dataclass
class LastRow:
    last_table: str
    id: int
    mdwiki_revid: int

    user: str
    title: str
    campaign: str
    cat: str
    lang: str
    target: str
    translate_type: str

    pupdate: str
    date: str
    add_date: str

    views: int

    deleted: bool = False
    word: int = 0

    @classmethod
    def from_row(cls, *, row: dict[str, Any], last_table: str) -> LastRow:
        """ """
        return cls(
            last_table=last_table,
            deleted=bool(row.get("deleted")),
            # date
            add_date=row.get("add_date") or "",
            date=row.get("date") or "",
            pupdate=row.get("pupdate") or "",
            # string
            campaign=row.get("campaign") or "",
            cat=row.get("cat") or "",
            lang=row.get("lang") or "",
            target=row.get("target") or "",
            title=row.get("title") or "",
            translate_type=row.get("translate_type") or "",
            user=row.get("user") or "",
            # int
            id=safe_int(row.get("id")),
            mdwiki_revid=safe_int(row.get("mdwiki_revid")),
            views=safe_int(row.get("views")),
            word=safe_int(row.get("word")),
        )

    @property
    def user_url(self) -> str:
        return url_for("leaderboard.users", username=self.user)

    @property
    def lang_url(self) -> str:
        return url_for("leaderboard.langs", lang_code=self.lang)

    @property
    def views_html(self) -> str:
        # Conditional parts are built as separate Markup fragments
        if self.last_table == "pages":
            return ViewsLinks.pageviews_link(self.views, self.lang, self.target, self.pupdate)

        return '<span class="text-muted">-</span>'

    @property
    def fix_url(self) -> str:
        return url_for(
            "fixrefs.process",
            mdwiki_revid=self.mdwiki_revid,
            source_title=self.title,
            lang=self.lang,
            title=self.target,
        )

    @property
    def email_url(self) -> str:
        return url_for(
            "coordinators_panel.email_msg.dashboard",
            user=self.user,
            id=self.id,
            last_table=self.last_table,
        )

    @property
    def draft_html(self) -> Markup:
        if self.add_date:
            return Markup(
                '<a href="https://mdwikicx.toolforge.org/wiki/{lang}/{title_q}" '
                'target="_blank" class="spannowrap">{date}</a>'
            ).format(
                lang=self.lang,
                title_q=_wiki_title(self.title),
                date=FormatTimestamps.format_date(self.add_date, format_str="%Y-%m-%d"),
            )

        return Markup('<span class="text-muted">-</span>')

    def render(self, index: int) -> Markup:
        display_user = self.user[:15] if len(self.user) > 15 else self.user

        return Markup("""
            <tr>
                <td>{index}</td>
                <td>
                    <a href="{user_url}" data-bs-toggle="tooltip" title="{user}">
                        {display_user}
                    </a>
                </td>
                <td>
                    <a class="btn btn-outline-primary btn-sm"
                       pup-target="{email_url}"
                       onclick="pup_window_email(this)">@</a>
                </td>
                <td>
                    <a href="https://mdwiki.org/wiki/{title_q}" target="_blank">
                        {title}
                    </a>
                </td>
                <td>{campaign}</td>
                <td>
                    <a href="{lang_url}">{lang}</a>:
                    <a href="https://{lang}.wikipedia.org/wiki/{target_q}" target="_blank">
                        {target}
                    </a>
                </td>
                <td>{pupdate}</td>
                <td>{views_html}</td>
                <td>
                    <a target="_blank" href="{fix_url}" class="spannowrap">Fix</a>
                </td>
                <td>{draft_html}</td>
                <td></td>
            </tr>
            """).format(
            index=index,
            user=self.user,
            display_user=display_user,
            title_q=_wiki_title(self.title),
            title=self.title,
            campaign=self.campaign or self.cat,
            lang=self.lang,
            target_q=_wiki_title(self.target),
            target=self.target,
            pupdate=self.pupdate,
            views_html=Markup(self.views_html),
            user_url=self.user_url,
            email_url=self.email_url,
            lang_url=self.lang_url,
            fix_url=self.fix_url,
            draft_html=self.draft_html,
        )

    def add_campaign(
        self,
        cats_to_camp: dict[str, str],
    ) -> None:
        if not self.cat or self.campaign:
            return

        if cats_to_camp.get(self.cat):
            self.campaign = cats_to_camp[self.cat]


__all__ = [
    "LastRow",
]
