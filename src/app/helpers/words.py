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
from functools import lru_cache
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


def _get_words_path() -> Path:
    """Get the path for the words.json file from config.

    Returns:
        Path to words.json file
    """
    return Path(settings.paths.words_json_path)


@lru_cache(maxsize=1)
def _load_words_table() -> dict[str, int]:
    """Load words table from JSON file.

    Returns:
        Dictionary mapping article titles to word counts
    """
    words_path = _get_words_path()

    try:
        if words_path.exists():
            with open(words_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure all values are integers using try-except for robust conversion
                result = {}
                for k, v in data.items():
                    try:
                        result[str(k)] = int(v)
                    except (ValueError, TypeError):
                        result[str(k)] = 0
                return result
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
