"""Utilities for managing words."""

from __future__ import annotations

import logging
from typing import List

from ....config import has_db_config, settings
from ..db.db_words import WordsDB
from .....db_models.public_models import WordRecord

logger = logging.getLogger(__name__)

_WORDS_STORE: WordsDB | None = None


def get_words_db() -> WordsDB:
    global _WORDS_STORE

    if _WORDS_STORE is None:
        if not has_db_config():
            raise RuntimeError("WordsDB requires database configuration; no fallback store is available.")

        try:
            _WORDS_STORE = WordsDB(settings.database_data)
        except Exception as exc:  # pragma: no cover - defensive guard for startup failures
            logger.exception("Failed to initialize MySQL WordsDB")
            raise RuntimeError("Unable to initialize WordsDB") from exc

    return _WORDS_STORE


def list_words() -> List[WordRecord]:
    """Return all word records."""
    store = get_words_db()
    return store.list()


def get_word(word_id: int) -> WordRecord | None:
    """Get a word record by ID."""
    store = get_words_db()
    return store.fetch_by_id(word_id)


def get_word_by_title(title: str) -> WordRecord | None:
    """Get a word record by title."""
    store = get_words_db()
    return store.fetch_by_title(title)


def add_word(
    w_title: str,
    w_lead_words: int | None = None,
    w_all_words: int | None = None,
) -> WordRecord:
    """Add a new word record."""
    store = get_words_db()
    return store.add(w_title, w_lead_words, w_all_words)


def add_or_update_word(
    w_title: str,
    w_lead_words: int | None = None,
    w_all_words: int | None = None,
) -> WordRecord:
    """Add or update a word record."""
    store = get_words_db()
    return store.add_or_update(w_title, w_lead_words, w_all_words)


def update_word(word_id: int, **kwargs) -> WordRecord:
    """Update a word record."""
    store = get_words_db()
    return store.update(word_id, **kwargs)


def delete_word(word_id: int) -> WordRecord:
    """Delete a word record by ID."""
    store = get_words_db()
    return store.delete(word_id)


def get_word_counts_for_title(title: str) -> tuple[int | None, int | None]:
    """Get lead and all word counts for a title."""
    store = get_words_db()
    record = store.fetch_by_title(title)
    if record:
        return record.w_lead_words, record.w_all_words
    return None, None


__all__ = [
    "get_words_db",
    "list_words",
    "get_word",
    "get_word_by_title",
    "add_word",
    "add_or_update_word",
    "update_word",
    "delete_word",
    "get_word_counts_for_title",
]
