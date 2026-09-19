"""Port of ``results_27/Tables/ExistsTable.php``.

Renders the table of already-existing pages. Mirrors PHP
``ExistsTable::render()``, but builds row dicts for the Jinja partial instead
of an HTML string.
"""

from __future__ import annotations

from typing import Any

from ..rows import ExistsRowBuilder


class ExistsTable:
    """Builds the rows of the Exists (already translated) table."""

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
        self._row_builder = ExistsRowBuilder()
        self._langcode = langcode
        self._cat = cat
        self._camp = camp
        self._user_coord = user_coord
        self._endpoint = endpoint
        self._user_is_logged_in = user_is_logged_in

    def build(self, items: dict[str, dict]) -> tuple[list[dict[str, Any]], int, int]:
        """Returns ``(rows, count_translated, count_translated_before)``."""
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

            rows.append(
                self._row_builder.build(
                    title=display_title,
                    counter=numb,
                    langcode=self._langcode,
                    cat=self._cat,
                    camp=self._camp,
                    target_tab=target_tab,
                    user_coord=self._user_coord,
                    endpoint=self._endpoint,
                    user_is_logged_in=self._user_is_logged_in,
                )
            )

            numb += 1

        return rows, count_translated, count_translated_before
