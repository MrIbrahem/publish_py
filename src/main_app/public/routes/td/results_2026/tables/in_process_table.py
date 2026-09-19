""" """

from __future__ import annotations

import logging
from typing import Any

from markupsafe import Markup

from ..rows import InProcessItem, InProcessRowBuilder

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
                    inprocess_button=self._row_builder.inprocess_button,
                    endpoint=self._row_builder.endpoint,
                )
            )

            numb += 1

        return rows

    @staticmethod
    def render(
        rows: list[InProcessItem],
        code: str,
        cat: str,
        camp: str,
        full_tr_user: bool,
        is_authenticated: bool,
        show_translate_header: bool = True,
    ) -> Markup:
        """Renders the in-process titles HTML table directly."""
        tbody_html = Markup("").join(
            row.render(code, cat, camp, full_tr_user, is_authenticated) for row in rows
        )
        translate_th = "<th><span>Translate</span></th>" if show_translate_header else "<th></th>"
        return Markup("""
            <table class="table compact table-striped table_100 table_text_left display table_responsive_main">
                <thead>
                    <tr>
                        <th class="num">#</th>
                        <th class="spannowrap" style="text-align: center">Title</th>
                        {translate_th}
                        <th class="spannowrap" style="text-align: center">
                            <span data-bs-toggle="tooltip"
                                data-bs-title="Page views in last month in English Wikipedia">Views</span>
                        </th>
                        <th class="spannowrap" style="text-align: center">
                            <span data-bs-toggle="tooltip"
                                data-bs-title="Page importance from medicine project in English Wikipedia">Importance</span>
                        </th>
                        <th class="spannowrap" style="text-align: center">
                            <span data-bs-toggle="tooltip" data-bs-title="Number of words of the article in mdwiki.org">Words</span>
                        </th>
                        <th class="spannowrap" style="text-align: center">
                            <span data-bs-toggle="tooltip"
                                data-bs-title="Number of references of the article in mdwiki.org">Refs.</span>
                        </th>
                        <th class="spannowrap" style="text-align: center">
                            <span data-bs-toggle="tooltip" data-bs-title="Wikidata identifier">Qid</span>
                        </th>
                        <th>user</th>
                        <th>date</th>
                    </tr>
                </thead>
                <tbody>
                    {tbody_html}
                </tbody>
            </table>
        """).format(
            translate_th=Markup(translate_th),
            tbody_html=tbody_html,
        )


__all__ = [
    "InProcessTable",
]
