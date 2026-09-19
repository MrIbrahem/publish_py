"""
Port of ``Tables/MissingTable.php``.

Renders the table of missing pages. Mirrors PHP ``MissingTable::render()``,
but builds :class:`MissingItem` rows for the Jinja partial instead of an
HTML string.
"""

from __future__ import annotations

import logging
from typing import Any

from ..rows import MissingItem

logger = logging.getLogger(__name__)


class MissingTable:
    """Builds the rows of the Results (missing) table."""

    def __init__(
        self,
        *,
        langcode: str,
        cat: str,
        camp: str,
        tra_type: str,
        full_tr_user: bool,
        user_is_logged_in: bool,
        translate_type_data: dict[str, dict[str, Any]],
    ) -> None:
        self._tra_type = tra_type or "lead"
        self._full_tr_user = full_tr_user
        self.translate_type_data = translate_type_data

    def build(self, items: list[dict]) -> list[MissingItem]:
        is_full_mode = self._tra_type == "all"

        # Sort by English page views (descending)
        sorted_items = sorted(items, key=lambda r: int(r.get("en_views") or 0), reverse=True)

        # PHP array_column($items, null, 'title') — keep last entry per title.
        items_by_title: dict[str, dict] = {}
        for row in sorted_items:
            title = row.get("title")
            if title:
                items_by_title[title] = row

        rows: list[MissingItem] = []
        numb = 1

        for title, title_data in items_by_title.items():
            if not title:
                continue

            display_title = title.replace("_", " ")

            translate_type_info = self.translate_type_data.get(display_title) or {"tt_lead": None, "tt_full": None}

            no_lead = translate_type_info["tt_lead"] == 0
            is_full_eligible = translate_type_info["tt_full"] == 1

            primary_row = MissingItem.from_row(
                title=display_title,
                row=title_data,
                counter=numb,
                is_full_row=False,
                tra_type=self._tra_type,
                translate_type_info=translate_type_info,
            )
            # Default stats of item: TranslateTypeRecord(tt_title=title, tt_lead=1, tt_full=0)

            # Skip lead filtering when full translation applies or user is allowed full access
            if is_full_mode or self._full_tr_user:
                rows.append(primary_row)
                numb += 1
                continue

            # PHP: "if ($no_lead && !$full) continue;"
            # no_lead and no full: TranslateTypeRecord(tt_title=title, tt_lead=0, tt_full=0)
            if no_lead and not is_full_eligible:
                continue

            if not no_lead:
                # When TranslateTypeRecord.tt_lead=0
                rows.append(primary_row)

            if is_full_eligible:
                # When TranslateTypeRecord.tt_full=1
                rows.append(
                    MissingItem.from_row(
                        title=display_title,
                        row=title_data,
                        counter=numb,
                        is_full_row=True,
                        tra_type="all",
                        translate_type_info=translate_type_info,
                    )
                )

            numb += 1

        return rows


__all__ = [
    "MissingTable",
]
