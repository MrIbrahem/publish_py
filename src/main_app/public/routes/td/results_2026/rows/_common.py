"""Shared row helpers for the results_27 row builders."""

from __future__ import annotations

from typing import Any


def _is_video(title: str) -> bool:
    """PHP ``str_starts_with(strtolower($title), "video:")``."""
    return title.lower().startswith("video:")


def _row_metrics(title_data: dict, tra_type: str) -> tuple[int, int, str, Any, str]:
    """Pick (words, refs, importance, en_views, qid) per PHP row builders.

    ``tra_type == "all"`` reads the whole-article counters; otherwise the
    lead-only counters are used.
    """
    if tra_type == "all":
        words = title_data.get("w_all_words") or 0
        refs = title_data.get("r_all_refs") or 0
    else:
        words = title_data.get("w_lead_words") or 0
        refs = title_data.get("r_lead_refs") or 0

    importance = title_data.get("importance") or "Unknown"
    en_views = title_data.get("en_views") if title_data.get("en_views") is not None else ""
    qid = title_data.get("qid") or ""
    return int(words or 0), int(refs or 0), importance, en_views, qid
