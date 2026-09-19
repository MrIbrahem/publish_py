"""Port of ``results_27/Tables/ExistsTable.php``.

Renders the table of already-existing pages. Mirrors PHP
``ExistsTable::render()``, but builds row dicts for the Jinja partial instead
of an HTML string.
"""

from __future__ import annotations

from typing import Any

from ..rows import ExistsItem, ExistsRowBuilder


class ExistsTable:
    """Builds a single row for the Exists results table."""

    def __init__(
        self,
        *,
        langcode: str,
        cat: str,
        camp: str,
        user_coord: bool,
        endpoint: str,
        user_is_logged_in: bool,
    ) -> None:
        self._row_builder = ExistsRowBuilder(
            langcode=langcode,
            cat=cat,
            camp=camp,
            user_coord=user_coord,
            endpoint=endpoint,
            user_is_logged_in=user_is_logged_in,
        )

    def build(self, items: dict[str, dict]) -> tuple[list[ExistsItem], int, int]:
        """Returns ``(rows, count_translated, count_translated_before)``."""
        rows: list[ExistsItem] = []
        numb = 1
        count_translated = 0
        count_translated_before = 0

        for title, target_tab in items.items():
            if not title:
                continue

            via = target_tab.get("via", "")

            if via == "td":
                count_translated += 1
            else:
                count_translated_before += 1

            row = ExistsItem.from_row(
                title=title,
                counter=numb,
                target_tab=target_tab,
                user_coord=self._row_builder.user_coord,
                endpoint=self._row_builder.endpoint,
            )

            rows.append(row)

            numb += 1

        return rows, count_translated, count_translated_before

    def count_status(self, items: dict[str, dict]) -> tuple[int, int]:
        """Returns ``(count_translated, count_translated_before)``."""
        count_translated = 0
        count_translated_before = 0

        for target_tab in items.values():
            via = target_tab.get("via", "")

            if via == "td":
                count_translated += 1
            else:
                count_translated_before += 1

        return count_translated, count_translated_before


__all__ = [
    "ExistsTable",
]
