"""Port of ``results_27/Helpers/TranslateTypeLoader.php``.

Loads the lists of titles that require full translation (``tt_full == 1``)
or do not allow lead-only translation (``tt_lead == 0``).
"""

from __future__ import annotations

import logging

from ......database.services import TranslateTypeService

logger = logging.getLogger(__name__)


class TranslateTypeLoader:
    """Loads the ``translate_type`` title sets used to filter the results table."""

    @staticmethod
    def load(type_: str) -> set[str]:
        """Return the ``"full"`` or ``"no"`` (no-lead) title set.

        Mirrors PHP ``TranslateTypeLoader::load("full"|"no")``. Any failure
        to read the table degrades to an empty set (matching the previous
        ``_load_translate_type_sets`` behavior).
        """
        full: set[str] = set()
        nolead: set[str] = set()

        try:
            service = TranslateTypeService()
            rows = service.list_translate_types()
        except Exception:
            logger.exception("Failed to load translate_type rows")
            return full if type_ == "full" else nolead

        for row in rows:
            if row.tt_full == 1:
                full.add(row.tt_title)
            if row.tt_lead == 0:
                nolead.add(row.tt_title)

        return full if type_ == "full" else nolead


__all__ = [
    "TranslateTypeLoader",
]
