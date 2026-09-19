"""
Python port of the PHP ``Results\\GetResults2026`` module.

Reference PHP files:
  - src/backend/results_2026/index.php           (results_loader_2026, Results_tables_2026, load_translate_type)
  - src/backend/results_2026/get_results_2026.php (get_results_2026, getinprocess_n)
  - src/backend/results_2026/results_table.php   (_make_one_row_results, make_results_table_2026)
  - src/backend/results_2026/results_table_exists.php (make_one_row_exists_2026, make_results_table_exists_2026)
  - src/backend/results_2026/results_table_inprocess.php (make_one_row_new_inprocess, make_results_table_inprocess)
  - src/results/helps.php                        (make_translate_urls)

The orchestrator returns a :class:`ResultsBundle` (the "results bundle") that
``templates/index.html`` consumes via three Jinja partials.
"""

from __future__ import annotations

import logging
from typing import Any

from ......services.utils.wiki_links import (
    content_translation_url,
    wikidata_link,
    wikipedia_link,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exists rows
# ---------------------------------------------------------------------------


class ExistsRowBuilder:
    """Builds a single row for the Exists results table."""

    def build(
        self,
        *,
        exists: dict[str, dict],
        langcode: str,
        cat: str,
        camp: str,
        user_coord: bool,
        endpoint: str,
        user_is_logged_in: bool,
    ) -> tuple[list[dict[str, Any]], int, int]:
        """Mirror of PHP ``make_results_table_exists_2026``.

        Returns ``(rows, count_translated, count_translated_before)``.
        """
        rows: list[dict[str, Any]] = []
        numb = 1
        count_translated = 0
        count_translated_before = 0

        for title, target_tab in exists.items():
            if not title:
                continue

            display_title = title.replace("_", " ")
            via = target_tab.get("via", "")
            target = target_tab.get("target") or ""

            if via == "td":
                count_translated += 1
            else:
                count_translated_before += 1

            translated_html = wikipedia_link(target, langcode) if (target and via == "td") else ""
            translated_before_html = wikipedia_link(target, langcode) if (target and via != "td") else ""

            # PHP: $tab is shown only when user_coord
            if user_coord:
                translate_url = content_translation_url(display_title, langcode, camp, "lead", endpoint)
                translate_html = (
                    "<div class='inline'>"
                    f"<a href='{translate_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
                    "</div>"
                )
            else:
                translate_html = ""

            rows.append(
                {
                    "n": str(numb),
                    "display_title": display_title,
                    "translate_html": translate_html,
                    "translated_html": translated_html,
                    "translated_before_html": translated_before_html,
                    "qid_html": wikidata_link(target_tab.get("qid") or ""),
                }
            )

            numb += 1

        return rows, count_translated, count_translated_before


__all__ = [
    "ExistsRowBuilder",
]
