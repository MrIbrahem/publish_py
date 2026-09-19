"""
Python port of the PHP ``Results\\GetResults27`` module.

Reference PHP files (``src/app/backend/results_27/``):
  - ResultsLoader.php            (ResultsLoader)
  - index.php                    (results_loader_27 — public entry point)
  - get_results_27.php           (get_results_27 — backward-compatible wrapper)
  - Data/ResultsFetcher.php      (ResultsFetcher)
  - Helpers/TranslateTypeLoader.php
  - Rows/{Missing,Exists,InProcess}RowBuilder.php
  - Tables/{Abstract,Missing,Exists,InProcess}Table.php

The orchestrator returns a :class:`.bundle.ResultsBundle` (the "results
bundle") that the ``results_2026`` Jinja partials consume. Unlike the PHP
original, this port produces no HTML — the card/table markup lives in the
templates.
"""

from __future__ import annotations

import logging

from .bundle import ResultsBundle
from .results_loader import ResultsLoader

logger = logging.getLogger(__name__)


def results_loader_27(
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
    """Public entry point — mirrors PHP ``results_loader_27(array $data)``."""
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
    "results_loader_27",
]
