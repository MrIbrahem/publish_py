""" """

from __future__ import annotations

import logging

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
        inprocess_button: str,
        full_tr_user: bool,
        titles_infos: dict[str, dict],
        endpoint: str,
    ) -> None:
        self._titles_infos = titles_infos
        self._inprocess_button = inprocess_button
        self._full_tr_user = full_tr_user
        self._endpoint = endpoint

    def build(self, items: dict[str, dict]) -> list[InProcessItem]:
        rows: list[InProcessItem] = []
        numb = 1

        for title, title_tab in items.items():
            if not title:
                continue

            display_title = title.replace("_", " ")
            title_data = self._titles_infos.get(title) or self._titles_infos.get(display_title) or {}

            rows.append(
                InProcessItem.from_row(
                    title=display_title,
                    counter=numb,
                    title_tab=title_tab,
                    title_data=title_data,
                    endpoint=self._endpoint,
                    inprocess_button=self._inprocess_button,
                    full_tr_user=self._full_tr_user,
                )
            )

            numb += 1

        return rows


__all__ = [
    "InProcessTable",
]
