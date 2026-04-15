"""Unit tests for helpers.words module.

Tests for word count lookup utilities.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from src.app_main.shared.utils.helpers.words import (
    _load_words_table,
    clear_words_cache,
    get_word_count,
)


class TestLoadWordsTable:
    """Tests for _load_words_table function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_words_cache()

    def test_loads_valid_json_file(self, tmp_path, monkeypatch):
        """Test loading a valid words JSON file."""
        words_data = {"Article1": 100, "Article2": 250, "Article3": 500}
        words_file = tmp_path / "words.json"
        words_file.write_text(json.dumps(words_data))

        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.__str__ = MagicMock(return_value=str(words_file))
        mock_path.__fspath__ = MagicMock(return_value=str(words_file))

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = words_file
            clear_words_cache()
            result = _load_words_table()

        assert result == words_data

    def test_returns_empty_dict_when_file_missing(self, monkeypatch):
        """Test that empty dict is returned when file doesn't exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = mock_path
            clear_words_cache()
            result = _load_words_table()

        assert result == {}

    def test_returns_empty_dict_on_json_decode_error(self, tmp_path, monkeypatch):
        """Test handling of invalid JSON."""
        words_file = tmp_path / "words.json"
        words_file.write_text("invalid json content")

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = words_file
            clear_words_cache()
            result = _load_words_table()

        assert result == {}

    def test_converts_string_values_to_integers(self, tmp_path, monkeypatch):
        """Test that string values are converted to integers."""
        words_data = {"Article1": "100", "Article2": "250"}
        words_file = tmp_path / "words.json"
        words_file.write_text(json.dumps(words_data))

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = words_file
            clear_words_cache()
            result = _load_words_table()

        assert result == {"Article1": 100, "Article2": 250}
        assert all(isinstance(v, int) for v in result.values())

    def test_handles_non_numeric_values_gracefully(self, tmp_path, monkeypatch):
        """Test that non-numeric values are converted to 0."""
        words_data = {"Article1": 100, "Article2": "not_a_number", "Article3": None}
        words_file = tmp_path / "words.json"
        words_file.write_text(json.dumps(words_data))

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = words_file
            clear_words_cache()
            result = _load_words_table()

        assert result["Article1"] == 100
        assert result["Article2"] == 0
        assert result["Article3"] == 0

    def test_caches_result(self, tmp_path, monkeypatch):
        """Test that results are cached."""
        words_data = {"Article1": 100}
        words_file = tmp_path / "words.json"
        words_file.write_text(json.dumps(words_data))

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = words_file
            clear_words_cache()

            # First call
            result1 = _load_words_table()
            # Second call should return cached value
            result2 = _load_words_table()

        assert result1 is result2  # Same object due to caching

    def test_returns_empty_dict_when_path_not_set(self, monkeypatch):
        """Test handling when words_json_path is not set."""
        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = None
            clear_words_cache()
            result = _load_words_table()

        assert result == {}


class TestGetWordCount:
    """Tests for get_word_count function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_words_cache()

    def test_returns_word_count_for_existing_title(self, tmp_path):
        """Test getting word count for an existing title."""
        words_data = {"TestArticle": 150}
        words_file = tmp_path / "words.json"
        words_file.write_text(json.dumps(words_data))

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = words_file
            clear_words_cache()
            result = get_word_count("TestArticle")

        assert result == 150

    def test_returns_zero_for_missing_title(self, tmp_path):
        """Test that 0 is returned for non-existent title."""
        words_data = {"OtherArticle": 100}
        words_file = tmp_path / "words.json"
        words_file.write_text(json.dumps(words_data))

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = words_file
            clear_words_cache()
            result = get_word_count("MissingArticle")

        assert result == 0

    def test_returns_zero_when_file_missing(self):
        """Test that 0 is returned when words file doesn't exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = mock_path
            clear_words_cache()
            result = get_word_count("AnyArticle")

        assert result == 0

    def test_case_sensitive_lookup(self, tmp_path):
        """Test that title lookup is case-sensitive."""
        words_data = {"TestArticle": 100, "testarticle": 200}
        words_file = tmp_path / "words.json"
        words_file.write_text(json.dumps(words_data))

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = words_file
            clear_words_cache()

            assert get_word_count("TestArticle") == 100
            assert get_word_count("testarticle") == 200


class TestClearWordsCache:
    """Tests for clear_words_cache function."""

    def test_clears_cached_data(self, tmp_path):
        """Test that cache is cleared properly."""
        words_data_v1 = {"Article1": 100}
        words_file = tmp_path / "words.json"
        words_file.write_text(json.dumps(words_data_v1))

        with patch("src.app_main.shared.utils.helpers.words.settings") as mock_settings:
            mock_settings.paths.words_json_path = words_file
            clear_words_cache()

            # Load initial data
            result1 = _load_words_table()
            assert result1["Article1"] == 100

            # Update file
            words_data_v2 = {"Article1": 200}
            words_file.write_text(json.dumps(words_data_v2))

            # Without clearing cache, should still return old value
            result2 = _load_words_table()
            assert result2["Article1"] == 100

            # After clearing cache, should return new value
            clear_words_cache()
            result3 = _load_words_table()
            assert result3["Article1"] == 200

    def test_safe_to_call_when_cache_empty(self):
        """Test that clearing empty cache doesn't raise error."""
        clear_words_cache()
        # Should not raise
        clear_words_cache()
