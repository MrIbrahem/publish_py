"""Port of ``results_27/Tables/ExistsTable.php``.

Renders the table of already-existing pages. Mirrors PHP
``ExistsTable::render()``, but builds row dicts for the Jinja partial instead
of an HTML string.
"""

from __future__ import annotations

from typing import Any

from markupsafe import Markup

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

    @staticmethod
    def render(
        rows: list[ExistsItem],
        translated_count: int,
        translated_before_count: int,
        code: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
    ) -> Markup:
        """Renders the existing titles HTML table directly."""
        tbody_html = Markup("").join(
            row.render(code, cat, camp, full_tr_user, is_authenticated) for row in rows
        )
        return Markup("""
            <table class="table compact table-striped table_100 table_text_left display table_responsive">
                <thead>
                    <tr>
                        <th class="num">#</th>
                        <th class="spannowrap" style="text-align: center">Title</th>
                        <th><span>Translate</span></th>
                        <th>Translated ({translated_count})</th>
                        <th>Translated before ({translated_before_count})</th>
                        <th class="spannowrap" style="text-align: center">
                            <span data-bs-toggle="tooltip" data-bs-title="Wikidata identifier">Qid</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {tbody_html}
                </tbody>
            </table>
        """).format(
            translated_count=translated_count,
            translated_before_count=translated_before_count,
            tbody_html=tbody_html,
        )


__all__ = [
    "ExistsTable",
]
