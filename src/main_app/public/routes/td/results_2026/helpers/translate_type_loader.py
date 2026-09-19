""" """

from __future__ import annotations

import logging

from ......database.services import TranslateTypeService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# load_translate_type — partition translate_type rows into the two sets
# ---------------------------------------------------------------------------


def load_translate_type_sets() -> tuple[set[str], set[str]]:
    """Mirror of PHP ``load_translate_type('no')`` + ``load_translate_type('full')``.

    Returns ``(nolead_titles, full_titles)``.
    """
    nolead: set[str] = set()
    full: set[str] = set()
    try:
        service = TranslateTypeService()
        rows = service.list_translate_types()
    except Exception:
        logger.exception("Failed to load translate_type rows")
        return nolead, full
    for row in rows:
        if row.tt_full == 1:
            full.add(row.tt_title)
        if row.tt_lead == 0:
            nolead.add(row.tt_title)
    return nolead, full


__all__ = [
    "load_translate_type_sets",
]
