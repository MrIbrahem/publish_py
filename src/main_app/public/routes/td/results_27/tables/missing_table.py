"""Port of ``results_27/Tables/MissingTable.php``.

Renders the table of missing pages. Mirrors PHP ``MissingTable::render()``,
but builds row dicts for the Jinja partial instead of an HTML string.
"""

from __future__ import annotations

from typing import Any

from ..rows import MissingRowBuilder


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
        nolead_titles: set[str],
        full_titles: set[str],
        user_is_logged_in: bool,
    ) -> None:
        self._row_builder = MissingRowBuilder()
        self._langcode = langcode
        self._cat = cat
        self._camp = camp
        self._tra_type = tra_type
        self._full_tr_user = full_tr_user
        self._nolead_titles = nolead_titles
        self._full_titles = full_titles
        self._user_is_logged_in = user_is_logged_in

    def build(self, items: list[dict]) -> list[dict[str, Any]]:
        do_full = (self._tra_type or "lead") != "all"

        # PHP usort by en_views desc.
        sorted_items = sorted(items, key=lambda r: int(r.get("en_views") or 0), reverse=True)

        # PHP array_column($items, null, 'title') — keep last entry per title.
        items_by_title: dict[str, dict] = {}
        for row in sorted_items:
            title = row.get("title")
            if title:
                items_by_title[title] = row

        rows: list[dict[str, Any]] = []
        numb = 1

        for title, title_data in items_by_title.items():
            if not title:
                continue
            # PHP str_replace('_', ' ', $title)
            display_title = title.replace("_", " ")

            primary_row = self._row_builder.build(
                title=display_title,
                title_data=title_data,
                counter=numb,
                is_full_row=False,
                tra_type=self._tra_type,
                langcode=self._langcode,
                cat=self._cat,
                camp=self._camp,
                full_tr_user=self._full_tr_user,
                user_is_logged_in=self._user_is_logged_in,
            )

            # PHP: "if (!$do_full || $full_tr_user) { emit and continue; }"
            if not do_full or self._full_tr_user:
                rows.append(primary_row)
                numb += 1
                continue

            no_lead = display_title in self._nolead_titles
            is_full_eligible = display_title in self._full_titles

            # PHP: "if ($no_lead && !$full) continue;"
            if no_lead and not is_full_eligible:
                continue

            if not no_lead:
                rows.append(primary_row)

            if is_full_eligible:
                rows.append(
                    self._row_builder.build(
                        title=display_title,
                        title_data=title_data,
                        counter=numb,
                        is_full_row=True,
                        tra_type="all",
                        langcode=self._langcode,
                        cat=self._cat,
                        camp=self._camp,
                        full_tr_user=self._full_tr_user,
                        user_is_logged_in=self._user_is_logged_in,
                    )
                )

            numb += 1

        return rows
