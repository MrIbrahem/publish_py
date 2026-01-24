"""Tests for helpers.words module."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.app.helpers.words import clear_words_cache, get_word_count


class TestGetWordCount:
    """Tests for get_word_count function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_words_cache()

    def test_returns_zero_when_file_not_found(self):
        """Test that 0 is returned when words.json doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"MAIN_DIR": tmpdir}):
                clear_words_cache()
                result = get_word_count("NonExistent Title")
                assert result == 0

    def test_returns_word_count_for_title(self):
        """Test that word count is returned for existing title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create words.json
            words_dir = Path(tmpdir) / "td" / "Tables" / "jsons"
            words_dir.mkdir(parents=True)
            words_file = words_dir / "words.json"

            words_data = {
                "Test Article": 1500,
                "Another Article": 2000,
            }
            with open(words_file, "w") as f:
                json.dump(words_data, f)

            with patch.dict(os.environ, {"MAIN_DIR": tmpdir}):
                clear_words_cache()
                result = get_word_count("Test Article")
                assert result == 1500

    def test_returns_zero_for_missing_title(self):
        """Test that 0 is returned for title not in words.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            words_dir = Path(tmpdir) / "td" / "Tables" / "jsons"
            words_dir.mkdir(parents=True)
            words_file = words_dir / "words.json"

            words_data = {"Test Article": 1500}
            with open(words_file, "w") as f:
                json.dump(words_data, f)

            with patch.dict(os.environ, {"MAIN_DIR": tmpdir}):
                clear_words_cache()
                result = get_word_count("Missing Article")
                assert result == 0

    def test_handles_words_json_path_env_var(self):
        """Test that WORDS_JSON_PATH env var is respected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            words_file = Path(tmpdir) / "custom_words.json"
            words_data = {"Custom Article": 3000}
            with open(words_file, "w") as f:
                json.dump(words_data, f)

            with patch.dict(os.environ, {"WORDS_JSON_PATH": str(words_file)}):
                clear_words_cache()
                result = get_word_count("Custom Article")
                assert result == 3000


class TestClearWordsCache:
    """Tests for clear_words_cache function."""

    def test_clears_cache(self):
        """Test that clear_words_cache clears the cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            words_dir = Path(tmpdir) / "td" / "Tables" / "jsons"
            words_dir.mkdir(parents=True)
            words_file = words_dir / "words.json"

            # First version
            words_data = {"Test": 100}
            with open(words_file, "w") as f:
                json.dump(words_data, f)

            with patch.dict(os.environ, {"MAIN_DIR": tmpdir}):
                clear_words_cache()
                assert get_word_count("Test") == 100

                # Update file
                words_data = {"Test": 200}
                with open(words_file, "w") as f:
                    json.dump(words_data, f)

                # Should still return old value due to cache
                assert get_word_count("Test") == 100

                # Clear cache and check new value
                clear_words_cache()
                assert get_word_count("Test") == 200
