""" """

from __future__ import annotations

import logging
from typing import Any

from flask import url_for

from ......services.utils.wiki_links import (
    tr_link_medwiki,
    wikidata_link,
)
from ..rows._common import _is_video, _row_metrics

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------


class MissingRowBuilder:
    """Builds a single row for the Missing results table."""

    def _missing_translate_html(
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
        """Mirror PHP ``_make_one_row_results`` — translate column HTML."""
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

    def _make_missing_row_dict(
        self,
        *,
        title: str,
        title_data: dict,
        count: int,
        is_full_row: bool,
        tra_type: str,
        langcode: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        user_is_logged_in: bool,
    ) -> dict[str, Any]:
        """Build one row dict for the Results table (PHP _make_one_row_results)."""
        is_video_title = _is_video(title)
        effective_tra_type = "all" if is_video_title else (tra_type or "lead")
        words, refs, importance, en_views, qid = _row_metrics(title_data, effective_tra_type)

        translate_html = self._missing_translate_html(
            title=title,
            langcode=langcode,
            cat=cat,
            camp=camp,
            tra_type=effective_tra_type,
            words=words,
            full_tr_user=full_tr_user,
            is_video_title=is_video_title,
            user_is_logged_in=user_is_logged_in,
        )

        # PHP "$count = $full && (substr != 'video:') ? '$count.Full' : $count"
        display_n: str = f"{count}.Full" if is_full_row and not is_video_title else str(count)

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

    def build(
        self,
        *,
        missing: list[dict],
        langcode: str,
        cat: str,
        camp: str,
        tra_type: str,
        full_tr_user: bool,
        nolead_titles: set[str],
        full_titles: set[str],
        user_is_logged_in: bool,
    ) -> list[dict[str, Any]]:
        """Mirror of PHP ``make_results_table_2026``."""
        do_full = (tra_type or "lead") != "all"

        # PHP usort by en_views desc.
        sorted_items = sorted(missing, key=lambda r: int(r.get("en_views") or 0), reverse=True)

        # PHP array_column($items, null, 'title') — keep last entry per title.
        items_by_title: dict[str, dict] = {}
        for row in sorted_items:
            title = row.get("title")
            if title:
                items_by_title[title] = row

        rows: list[dict[str, Any]] = []
        numb = 1

        for title, title_data in items_by_title.items():
            if not title:
                continue
            # PHP str_replace('_', ' ', $title)
            display_title = title.replace("_", " ")

            primary_row = self._make_missing_row_dict(
                title=display_title,
                title_data=title_data,
                count=numb,
                is_full_row=False,
                tra_type=tra_type,
                langcode=langcode,
                cat=cat,
                camp=camp,
                full_tr_user=full_tr_user,
                user_is_logged_in=user_is_logged_in,
            )

            # PHP: "if (!$do_full || $full_tr_user) { emit and continue; }"
            if not do_full or full_tr_user:
                rows.append(primary_row)
                numb += 1
                continue

            no_lead = display_title in nolead_titles
            is_full_eligible = display_title in full_titles

            # PHP: "if ($no_lead && !$full) continue;"
            if no_lead and not is_full_eligible:
                continue

            if not no_lead:
                rows.append(primary_row)

            if is_full_eligible:
                rows.append(
                    self._make_missing_row_dict(
                        title=display_title,
                        title_data=title_data,
                        count=numb,
                        is_full_row=True,
                        tra_type="all",
                        langcode=langcode,
                        cat=cat,
                        camp=camp,
                        full_tr_user=full_tr_user,
                        user_is_logged_in=user_is_logged_in,
                    )
                )

            numb += 1

        return rows
