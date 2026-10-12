"""Port of ``results_27/Tables/ExistsTable.php``.

Renders the table of already-existing pages. Mirrors PHP
``ExistsTable::render()``, but builds :class:`ExistsItem` rows for the Jinja
partial instead of an HTML string.
"""

from __future__ import annotations

from typing import Any

from ..mapping import ExistsItem


class ExistsTable:
    """Builds the rows of the Exists results table."""

    def __init__(
        self,
        *,
        translate_type_data: dict[str, dict[str, Any]],
    ) -> None:
        self.translate_type_data = translate_type_data

    def build(self, items: dict[str, dict]) -> list[ExistsItem]:
        """Returns ``rows``."""
        rows: list[ExistsItem] = []
        numb = 1

        for title, target_tab in items.items():
            if not title:
                continue

            display_title = title.replace("_", " ")
            translate_type_info = self.translate_type_data.get(display_title) or {"tt_lead": None, "tt_full": None}

            rows.append(
                ExistsItem.from_row(
                    title=title,
                    counter=numb,
                    row=target_tab,
                    translate_type_info=translate_type_info,
                )
            )

            numb += 1

        return rows

    def count_status(self, exists_rows: list[ExistsItem]) -> tuple[int, int]:
        """Returns ``(count_translated, count_translated_before)``."""

        count_translated = len([x for x in exists_rows if x.via == "td"])
        count_translated_before = len([x for x in exists_rows if x.via != "td"])

        return count_translated, count_translated_before


__all__ = [
    "ExistsTable",
]
