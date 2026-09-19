"""
Python port of the PHP ``Results\\GetResults2026`` module.

Reference PHP files:
  - src/backend/results_2026/index.php           (results_loader_2026, Results_tables_2026, load_translate_type)
  - src/backend/results_2026/get_results_2026.php (get_results_2026, getinprocess_n)
  - src/backend/results_2026/results_table.php   (_make_one_row_results, make_results_table_2026)
  - src/backend/results_2026/results_table_exists.php (make_one_row_exists_2026, make_results_table_exists_2026)
  - src/backend/results_2026/results_table_inprocess.php (make_one_row_new_inprocess, make_results_table_inprocess)
  - src/results/helps.php                        (make_translate_urls)

The orchestrator returns a :class:`ResultsBundle` (the "results bundle") that
``templates/index.html`` consumes via three Jinja partials.
"""

from __future__ import annotations

import logging

from .bundle import ResultsBundle
from .results_loader import ResultsLoader

logger = logging.getLogger(__name__)


def results_loader_2026(
    *,
    code: str,
    camp: str,
    cat: str,
    tra_type: str,
    code_lang_name: str,
    user_coord: bool,
    settings: dict[str, bool],
    full_tr_user: bool,
    user_is_logged_in: bool,
) -> ResultsBundle:
    """
    Build the results bundle for the index page.

    Mirrors PHP ``results_loader_2026($data)`` + ``Results_tables_2026(...)``.
    Returns a :class:`ResultsBundle` with the data the Jinja templates need;
    produces no HTML side effects of its own.
    """
    return ResultsLoader().load(
        code=code,
        camp=camp,
        cat=cat,
        tra_type=tra_type,
        code_lang_name=code_lang_name,
        user_coord=user_coord,
        settings=settings,
        full_tr_user=full_tr_user,
        user_is_logged_in=user_is_logged_in,
    )


__all__ = [
    "results_loader_2026",
]
