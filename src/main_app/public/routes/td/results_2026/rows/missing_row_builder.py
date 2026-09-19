""" """

from __future__ import annotations

import logging
from typing import Any

from flask import url_for

from .mapping import MissingItem

from ......services.utils.wiki_links import (
    tr_link_medwiki,
    wikidata_link,
)
from ._common import _is_video, _row_metrics

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------

class MissingRowBuilder:
    """Builds a single row for the Missing results table."""

    def __init__(
        self,
        *,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        user_is_logged_in: bool,
    ) -> None:
        self.langcode = langcode
        self.cat = cat
        self.camp = camp
        self.full_tr_user = full_tr_user
        self.user_is_logged_in = user_is_logged_in

    def build(
        self,
        *,
        title: str,
        counter: int,
        is_full_row: bool,
        title_data: dict,
        tra_type: str,
    ) -> dict[str, Any]:

        is_video_title = _is_video(title)
        if is_video_title:
            tra_type = "all"

        words, refs, importance, en_views, qid = _row_metrics(title_data, tra_type)

        translate_html = self._translate_html(
            title=title,
            tra_type=tra_type,
            words=words,
            is_video_title=is_video_title,
        )

        # PHP "$count = $full && (substr != 'video:') ? '$count.Full' : $count"
        display_n: str = f"{counter}.Full" if is_full_row and not is_video_title else str(counter)

        return {
            "n": display_n,
            "title": title,
            "translate_html": translate_html,
            "en_views": en_views,
            "importance": importance,
            "words": words,
            "refs": refs,
            "qid_html": wikidata_link(qid),
            "is_full_row": is_full_row,
        }

    def _translate_html(
        self,
        *,
        title: str,
        tra_type: str,
        words: int,
        is_video_title: bool,
    ) -> str:
        """PHP ``_make_one_row_results`` — translate column HTML."""
        # logic from results_table.php — anonymous user
        if not self.user_is_logged_in:
            login_url = url_for("auth.login")
            return f"<a href='{login_url}' class='btn btn-outline-primary btn-sm'>Login</a>"

        full_url = tr_link_medwiki(title, self.langcode, self.cat, self.camp, "all", words)
        lead_url = tr_link_medwiki(title, self.langcode, self.cat, self.camp, tra_type, words)

        if self.full_tr_user and not is_video_title:
            return (
                "<div class='inline'>"
                f"<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Lead</a>"
                f"<a href='{full_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Full</a>"
                "</div>"
            )

        return f"<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"

__all__ = [
    "MissingRowBuilder",
]
