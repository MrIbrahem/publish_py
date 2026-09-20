""" """

from __future__ import annotations

import logging
from typing import Any

from ..mapping.inprocess_mapping import InProcessItem

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# In-process table
# ---------------------------------------------------------------------------


class InProcessTable:
    """Builds the rows of the In-process table."""

    def __init__(
        self,
        *,
        titles_infos: dict[str, dict],
        translate_type_data: dict[str, dict[str, Any]],
    ) -> None:
        self.translate_type_data = translate_type_data
        self._titles_infos = titles_infos

    def build(self, items: dict[str, dict]) -> list[InProcessItem]:
        rows: list[InProcessItem] = []
        numb = 1

        for title, title_tab in items.items():
            if not title:
                continue

            display_title = title.replace("_", " ")
            translate_type_info = self.translate_type_data.get(display_title) or {"tt_lead": None, "tt_full": None}

            title_data = self._titles_infos.get(title) or self._titles_infos.get(display_title) or {}

            rows.append(
                InProcessItem.from_row(
                    title=display_title,
                    counter=numb,
                    title_tab=title_tab,
                    row=title_data,
                    translate_type_info=translate_type_info,
                )
            )

            numb += 1

        return rows


__all__ = [
    "InProcessTable",
]
