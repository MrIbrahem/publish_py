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

    def build(
        self,
        *,
        inprocess: dict[str, dict],
        langcode: str,
        cat: str,
        camp: str,
        tra_btn: str,
        full_tr_user: bool,
        titles_infos: dict[str, dict],
        endpoint: str,
        user_is_logged_in: bool,
    ) -> list[dict[str, Any]]:
        """Mirror of PHP ``make_results_table_inprocess``."""
        rows: list[dict[str, Any]] = []
        numb = 1

        for title, title_tab in inprocess.items():
            if not title:
                continue

            display_title = title.replace("_", " ")
            title_data = titles_infos.get(title) or titles_infos.get(display_title) or {}

            tra_type = title_tab.get("translate_type") or ""
            is_video_title = _is_video(display_title)
            if is_video_title:
                tra_type = "all"

            words, refs, importance, en_views, qid = _row_metrics(title_data, tra_type or "lead")

            user = title_tab.get("user") or ""

            translate_html = self._translate_html(
                title=display_title,
                tra_type=tra_type,
                langcode=langcode,
                cat=cat,
                camp=camp,
                words=words,
                tra_btn=tra_btn,
                full_tr_user=full_tr_user,
                is_video_title=is_video_title,
                endpoint=endpoint,
            )

            rows.append(
                {
                    "n": str(numb),
                    "title": display_title,
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
            )

            numb += 1

        return rows

    def _translate_html(
        self,
        *,
        title: str,
        tra_type: str,
        langcode: str,
        cat: str,
        camp: str,
        words: int,
        tra_btn: str,
        full_tr_user: bool,
        is_video_title: bool,
        endpoint: str,
    ) -> str:
        """Mirror of PHP ``make_translate_urls`` — inprocess branch only.

        Returns the HTML for the Translate column. When the button is disabled
        or no user is logged in, returns an empty string (the column then
        renders blank).
        """
        if tra_btn != "1":
            return ""

        effective_type = "all" if is_video_title else (tra_type or "lead")
        full_url = content_translation_url(title, langcode, camp, "all", endpoint)
        lead_url = content_translation_url(title, langcode, camp, effective_type, endpoint)

        tab = f"<a href='{lead_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
        if full_tr_user and not is_video_title:
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
