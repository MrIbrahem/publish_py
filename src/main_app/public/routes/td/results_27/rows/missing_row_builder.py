"""Port of ``results_27/Rows/MissingRowBuilder.php``.

Builds one row dict for the Results (missing) table. Mirrors PHP
``MissingRowBuilder::build()``, but returns data for the Jinja partial
instead of an HTML string.
"""

from __future__ import annotations

from typing import Any

from flask import url_for

from ......services.utils.wiki_links import tr_link_medwiki, wikidata_link

from ._common import _is_video, _row_metrics


class MissingRowBuilder:
    """Builds a single row for the Missing results table."""

    def build(
        self,
        *,
        title: str,
        tra_type: str,
        counter: int,
        langcode: str,
        cat: str,
        camp: str,
        is_full_row: bool,
        full_tr_user: bool,
        user_is_logged_in: bool,
        title_data: dict,
    ) -> dict[str, Any]:
        if not tra_type:
            tra_type = "lead"

        is_video_title = _is_video(title)
        if is_video_title:
            tra_type = "all"

        words, refs, importance, en_views, qid = _row_metrics(title_data, tra_type)

        translate_html = self._translate_html(
            title=title,
            langcode=langcode,
            cat=cat,
            camp=camp,
            tra_type=tra_type,
            words=words,
            full_tr_user=full_tr_user,
            is_video_title=is_video_title,
            user_is_logged_in=user_is_logged_in,
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
        langcode: str,
        cat: str,
        camp: str,
        tra_type: str,
        words: int,
        full_tr_user: bool,
        is_video_title: bool,
        user_is_logged_in: bool,
    ) -> str:
        """PHP ``_make_one_row_results`` translate column HTML."""
        # logic from results_table.php — anonymous user
        if not user_is_logged_in:
            login_url = url_for("auth.login")
            return f"<a href='{login_url}' class='btn btn-outline-primary btn-sm'>Login</a>"

        full_url = tr_link_medwiki(title, langcode, cat, camp, "all", words)
        lead_url = tr_link_medwiki(title, langcode, cat, camp, tra_type, words)

        if full_tr_user and not is_video_title:
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
