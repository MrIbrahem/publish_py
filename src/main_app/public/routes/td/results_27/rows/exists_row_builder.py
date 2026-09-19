"""Port of ``results_27/Rows/ExistsRowBuilder.php``.

Builds one row dict for the Exists (already translated) table. Mirrors PHP
``ExistsRowBuilder::build()``, but returns data for the Jinja partial
instead of an HTML string.
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
        title: str,
        counter: int,
        langcode: str,
        cat: str,
        camp: str,
        target_tab: dict,
        user_coord: bool,
        endpoint: str,
        user_is_logged_in: bool,
    ) -> dict[str, Any]:
        via = target_tab.get("via", "")
        target = target_tab.get("target") or ""

        translated_html = wikipedia_link(target, langcode) if (target and via == "td") else ""
        translated_before_html = wikipedia_link(target, langcode) if (target and via != "td") else ""

        # PHP: $tab is shown only when user_coord
        if user_coord:
            translate_url = content_translation_url(title, langcode, camp, "lead", endpoint)
            translate_html = (
                "<div class='inline'>"
                f"<a href='{translate_url}' class='btn btn-outline-primary btn-sm' target='_blank'>Translate</a>"
                "</div>"
            )
        else:
            translate_html = ""

        return {
            "n": str(counter),
            "display_title": title,
            "translate_html": translate_html,
            "translated_html": translated_html,
            "translated_before_html": translated_before_html,
            "qid_html": wikidata_link(target_tab.get("qid") or ""),
        }


__all__ = [
    "ExistsRowBuilder",
]
