""" """

from __future__ import annotations

import logging
from typing import Any

from ......services.utils.wiki_links import (
    content_translation_url,
    wikidata_link,
)
from ._common import _is_video, _row_metrics

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-process rows
# ---------------------------------------------------------------------------


def _format_inprocess_date(value: Any) -> str:
    """Mirror of PHP ``if (strpos($_date_, ':') !== false) explode(' ', $_date_)[0]``."""
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        # datetime → ISO; PHP receives "YYYY-MM-DD HH:MM:SS".
        text = value.isoformat(sep=" ")
    else:
        text = str(value)
    if ":" in text:
        return text.split(" ", 1)[0]
    return text


class InProcessRowBuilder:
    """Builds a single row for the In-process results table."""

    def __init__(
        self,
        *,
        langcode: str,
        cat: str,
        camp: str,
        user_is_logged_in: bool,
        full_tr_user: bool,
        endpoint: str,
        show_translation_button: str,
    ) -> None:
        self.langcode = langcode
        self.cat = cat
        self.camp = camp
        self.full_tr_user = full_tr_user
        self.user_is_logged_in = user_is_logged_in
        self.endpoint = endpoint
        self.show_translation_button = show_translation_button

    def build(
        self,
        *,
        title_tab: dict[str, Any],
        title: str,
        counter: int,
        title_data: dict[str, Any],
    ) -> dict[str, Any]:
        tra_type = title_tab.get("translate_type") or "lead"
        is_video_title = _is_video(title)
        if is_video_title:
            tra_type = "all"

        words, refs, importance, en_views, qid = _row_metrics(title_data, tra_type)

        user = title_tab.get("user") or ""

        translate_html = self._translate_html(
            title=title,
            tra_type=tra_type,
            words=words,
            is_video_title=is_video_title,
        )

        return {
            "n": str(counter),
            "title": title,
            "translate_html": translate_html,
            "en_views": en_views,
            "importance": importance,
            "words": words,
            "refs": refs,
            "qid_html": wikidata_link(qid),
            "user": user,
            "date": _format_inprocess_date(title_tab.get("add_date") or title_tab.get("date")),
            "is_full_row": False,
        }

    def _translate_html(
        self,
        *,
        title: str,
        tra_type: str,
        words: int,
        is_video_title: bool,
    ) -> str:
        """
        PHP ``make_translate_urls`` — inprocess branch only.

        Returns the HTML for the Translate column. When the button is disabled
        or no user is logged in, returns an empty string (the column then
        renders blank).
        """
        if self.show_translation_button != "1":
            return ""

        effective_type = "all" if is_video_title else (tra_type or "lead")
        full_url = content_translation_url(title, self.langcode, self.camp, "all", self.endpoint)
        lead_url = content_translation_url(title, self.langcode, self.camp, effective_type, self.endpoint)

        tab = f"<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
        if self.full_tr_user and not is_video_title:
            tab = (
                "<div class='inline'>"
                f"<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Lead</a>"
                f"<a href='{full_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Full</a>"
                "</div>"
            )
        return tab


__all__ = [
    "InProcessRowBuilder",
]
