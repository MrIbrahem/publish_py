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

from .bundle import ResultsBundle
from .data import ResultsFetcher
from .loader import results_loader_27
from .results_loader import ResultsLoader

__all__ = [
    "results_loader_27",
    "ResultsLoader",
    "ResultsBundle",
    "ResultsFetcher",
]
