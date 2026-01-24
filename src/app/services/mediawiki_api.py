"""MediaWiki API client for edit operations.

Mirrors: php_src/bots/api/do_edit.php
"""

import json
import logging
from typing import Any

from .oauth_client import post_params

logger = logging.getLogger(__name__)


def publish_do_edit(
    api_params: dict[str, Any],
    wiki: str,
    access_key: str,
    access_secret: str,
) -> dict[str, Any]:
    """Publish an edit to MediaWiki.

    Args:
        api_params: API parameters for the edit
        wiki: Wiki language code
        access_key: OAuth access key
        access_secret: OAuth access secret

    Returns:
        Edit result as dictionary
    """
    https_domain = f"https://{wiki}.wikipedia.org"
    response = post_params(api_params, https_domain, access_key, access_secret)

    try:
        result = json.loads(response) if response else {}
    except json.JSONDecodeError:
        logger.error(f"Failed to parse edit response: {response}")
        result = {"error": "Failed to parse response"}

    return result
