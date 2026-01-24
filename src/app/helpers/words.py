"""Words table lookup utilities.

Mirrors: php_src/bots/words lookup

This module provides word count lookup for articles from a JSON file.

PHP implementation:
```php
$word_file = __DIR__ . "/../../td/Tables/jsons/words.json";
$Words_table = json_decode(file_get_contents($word_file), true);
$word = $Words_table[$title] ?? 0;
```
"""

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _get_default_words_path() -> Path:
    """Get the default path for the words.json file.

    Returns:
        Path to words.json file
    """
    # Check environment variable first
    words_path = os.getenv("WORDS_JSON_PATH")
    if words_path:
        return Path(words_path)

    # Default paths to check (in order of priority)
    main_dir = os.getenv("MAIN_DIR", os.path.expanduser("~/data"))
    possible_paths = [
        Path(main_dir) / "td" / "Tables" / "jsons" / "words.json",
        Path(main_dir) / "words.json",
        Path(__file__).parent.parent.parent.parent / "data" / "words.json",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    # Return default path even if it doesn't exist
    return Path(main_dir) / "td" / "Tables" / "jsons" / "words.json"


@lru_cache(maxsize=1)
def _load_words_table() -> dict[str, int]:
    """Load words table from JSON file.

    Returns:
        Dictionary mapping article titles to word counts
    """
    words_path = _get_default_words_path()

    try:
        if words_path.exists():
            with open(words_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure all values are integers
                return {str(k): int(v) if isinstance(v, (int, float, str)) and str(v).isdigit() else 0 for k, v in data.items()}
        else:
            logger.debug(f"Words file not found at {words_path}")
            return {}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse words.json: {e}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load words table from {words_path}: {e}")
        return {}


def get_word_count(title: str) -> int:
    """Get word count for an article title.

    Mirrors PHP:
    ```php
    $word = $Words_table[$title] ?? 0;
    ```

    Args:
        title: Article title

    Returns:
        Word count for the title, or 0 if not found
    """
    words_table = _load_words_table()
    return words_table.get(title, 0)


def clear_words_cache() -> None:
    """Clear the cached words table.

    Call this if the words.json file is updated.
    """
    _load_words_table.cache_clear()


__all__ = [
    "get_word_count",
    "clear_words_cache",
]
