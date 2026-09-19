"""
Port of ``results_27/Helpers/TranslateTypeLoader.php``.

Loads the lists of titles that require full translation (``tt_full == 1``)
or do not allow lead-only translation (``tt_lead == 0``).
"""

from __future__ import annotations

import logging

from ......database.models import TranslateTypeRecord
from ......database.services import TranslateTypeService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# load_translate_type — partition translate_type rows into the two sets
# ---------------------------------------------------------------------------


class TranslateTypeLoader:
    """Loads the ``translate_type`` title sets used to filter the results table."""

    def __init__(self) -> None:
        self.rows: list[TranslateTypeRecord] = []
        self.rows_data: dict[str, dict[str, int]] = {}

    def _load(self) -> None:
        if self.rows:
            return
        try:
            service = TranslateTypeService()
            self.rows = service.list_translate_types()
            self.rows_data = {row.tt_title: row.to_json() for row in self.rows}

        except Exception:
            logger.exception("Failed to load translate_type rows")

    def load(self, type_: str) -> set[str]:
        """Return the ``"full"`` or ``"no"`` (no-lead) title set.

        Mirrors PHP ``TranslateTypeLoader::load("full"|"no")``. Any failure
        to read the table degrades to an empty set (matching the previous
        ``_load_translate_type_sets`` behavior).
        """
        self._load()

        full: set[str] = set()
        nolead: set[str] = set()

        for row in self.rows:
            if row.tt_full == 1:
                full.add(row.tt_title)
            if row.tt_lead == 0:
                nolead.add(row.tt_title)

        return full if type_ == "full" else nolead


__all__ = [
    "TranslateTypeLoader",
]
