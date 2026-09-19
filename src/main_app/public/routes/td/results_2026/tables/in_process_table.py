""" """

from __future__ import annotations

import logging
from typing import Any

from ..rows import InProcessRowBuilder

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# In-process table
# ---------------------------------------------------------------------------


class InProcessTable:
    """Builds the rows of the In-process table."""

    def __init__(
        self,
        *,
        langcode: str,
        cat: str,
        camp: str,
        inprocess_button: str,
        full_tr_user: bool,
        titles_infos: dict[str, dict],
        endpoint: str,
        user_is_logged_in: bool,
    ) -> None:
        self._titles_infos = titles_infos
        self._row_builder = InProcessRowBuilder(
            langcode=langcode,
            cat=cat,
            camp=camp,
            full_tr_user=full_tr_user,
            user_is_logged_in=user_is_logged_in,
            inprocess_button=inprocess_button,
            endpoint=endpoint,
        )

    def build(self, items: dict[str, dict]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        numb = 1

        for title, title_tab in items.items():
            if not title:
                continue

            display_title = title.replace("_", " ")
            title_data = self._titles_infos.get(title) or self._titles_infos.get(display_title) or {}

            rows.append(
                self._row_builder.build(
                    title=display_title,
                    counter=numb,
                    title_tab=title_tab,
                    title_data=title_data,
                )
            )

            numb += 1

        return rows


__all__ = [
    "InProcessTable",
]
