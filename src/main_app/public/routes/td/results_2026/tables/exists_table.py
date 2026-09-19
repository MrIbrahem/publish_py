"""Port of ``results_27/Tables/ExistsTable.php``.

Renders the table of already-existing pages. Mirrors PHP
``ExistsTable::render()``, but builds row dicts for the Jinja partial instead
of an HTML string.
"""

from __future__ import annotations

from typing import Any

from ..rows import ExistsRowBuilder


class ExistsTable:
    """Builds a single row for the Exists results table."""

    def build(
        self,
        *,
        items: dict[str, dict],
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

        for title, target_tab in items.items():
            if not title:
                continue

            display_title = title.replace("_", " ")
            via = target_tab.get("via", "")

            if via == "td":
                count_translated += 1
            else:
                count_translated_before += 1

            row = self.build_row(
                langcode,
                camp,
                user_coord,
                endpoint,
                numb,
                target_tab,
                display_title,
                via,
            )

            rows.append(row)

            numb += 1

        return rows, count_translated, count_translated_before


__all__ = [
    "ExistsRowBuilder",
]
