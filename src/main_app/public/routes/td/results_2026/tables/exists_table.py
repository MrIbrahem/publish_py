"""Port of ``results_27/Tables/ExistsTable.php``.

Renders the table of already-existing pages. Mirrors PHP
``ExistsTable::render()``, but builds :class:`ExistsItem` rows for the Jinja
partial instead of an HTML string.
"""

from __future__ import annotations

from ..mapping import ExistsItem


class ExistsTable:
    """Builds the rows of the Exists results table."""

    def __init__(
        self,
        *,
        user_coord: bool,
        endpoint: str,
    ) -> None:
        self._user_coord = user_coord
        self._endpoint = endpoint

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

            rows.append(
                ExistsItem.from_row(
                    title=title,
                    counter=numb,
                    target_tab=target_tab,
                    endpoint=self._endpoint,
                    user_coord=self._user_coord,
                )
            )

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
