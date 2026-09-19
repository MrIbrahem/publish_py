"""Port of ``results_27/Tables/InProcessTable.php``.

Renders the table of pages currently being translated. Mirrors PHP
``InProcessTable::render()``, but builds row dicts for the Jinja partial
instead of an HTML string.
"""

from __future__ import annotations

from typing import Any

from ..rows import InProcessRowBuilder


class InProcessTable:
    """Builds the rows of the In-process table."""

    def __init__(
        self,
        *,
        langcode: str,
        cat: str,
        camp: str,
        tra_btn: str,
        full_tr_user: bool,
        titles_infos: dict[str, dict],
        endpoint: str,
        user_is_logged_in: bool,
    ) -> None:
        self._row_builder = InProcessRowBuilder()
        self._langcode = langcode
        self._cat = cat
        self._camp = camp
        self._tra_btn = tra_btn
        self._full_tr_user = full_tr_user
        self._titles_infos = titles_infos
        self._endpoint = endpoint
        self._user_is_logged_in = user_is_logged_in

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
                    langcode=self._langcode,
                    cat=self._cat,
                    camp=self._camp,
                    title_tab=title_tab,
                    full_tr_user=self._full_tr_user,
                    title_data=title_data,
                    endpoint=self._endpoint,
                    tra_btn=self._tra_btn,
                    user_is_logged_in=self._user_is_logged_in,
                )
            )

            numb += 1

        return rows
