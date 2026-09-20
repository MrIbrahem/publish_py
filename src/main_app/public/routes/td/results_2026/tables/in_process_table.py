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
        # titles_infos: dict[str, dict],
        translate_type_data: dict[str, dict[str, Any]],
    ) -> None:
        self.translate_type_data = translate_type_data
        # self._titles_infos = titles_infos

    def build(self, items: dict[str, dict]) -> list[InProcessItem]:
        rows: list[InProcessItem] = []
        numb = 1

        for title, row in items.items():
            if not title:
                continue

            display_title = title.replace("_", " ")
            translate_type_info = self.translate_type_data.get(display_title) or {"tt_lead": None, "tt_full": None}

            # row = self._titles_infos.get(title) or self._titles_infos.get(display_title) or {}
            # row.update({x: v for x, v in title_tab.items() if x and v and not row.get(x)})

            rows.append(
                InProcessItem.from_row(
                    title=display_title,
                    counter=numb,
                    row=row,
                    translate_type_info=translate_type_info,
                )
            )

            numb += 1

        return rows


__all__ = [
    "InProcessTable",
]
