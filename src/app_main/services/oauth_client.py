"""MediaWiki OAuth client wrapper.

Mirrors: php_src/bots/api/get_token.php
"""

import json
import logging
from typing import Any

import requests
from requests_oauthlib import OAuth1

from ..config import settings

logger = logging.getLogger(__name__)


def get_oauth_client(access_key: str, access_secret: str, domain: str = "en.wikipedia.org") -> OAuth1:
    """Create OAuth1 session for MediaWiki API.

    Args:
        access_key: User's OAuth access key
        access_secret: User's OAuth access secret
        domain: Wiki domain (e.g., 'en.wikipedia.org')

    Returns:
        OAuth1 authentication object
    """
    return OAuth1(
        settings.oauth.consumer_key,
        client_secret=settings.oauth.consumer_secret,
        resource_owner_key=access_key,
        resource_owner_secret=access_secret,
    )


def get_csrf_token(access_key: str, access_secret: str, wiki: str = "en") -> dict[str, Any]:
    """Get CSRF token from MediaWiki API.

    Args:
        access_key: OAuth access key
        access_secret: OAuth access secret
        wiki: Wiki language code (e.g., 'en')

    Returns:
        API response as dictionary containing token data
    """
    api_url = f"https://{wiki}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "meta": "tokens",
        "format": "json",
    }

    client = get_oauth_client(access_key, access_secret, f"{wiki}.wikipedia.org")
    response = requests.get(api_url, params=params, auth=client, timeout=30)
    return response.json()


def post_params(
    api_params: dict[str, Any],
    https_domain: str,
    access_key: str,
    access_secret: str,
) -> str:
    """Make OAuth POST request to MediaWiki API.

    Args:
        api_params: API parameters for the request
        https_domain: Full domain URL (e.g., 'https://en.wikipedia.org')
        access_key: OAuth access key
        access_secret: OAuth access secret

    Returns:
        Response text from API
    """
    api_url = f"{https_domain}/w/api.php"

    # Extract wiki language from domain
    domain_parts = https_domain.replace("https://", "").split(".")
    wiki = domain_parts[0] if domain_parts else "en"

    # Get CSRF token
    csrf_data = get_csrf_token(access_key, access_secret, wiki)

    if "error" in csrf_data:
        logger.error(f"CSRF token error: {csrf_data}")
        return json.dumps({"error": "get_csrf_token failed", "csrftoken_data": csrf_data})

    csrf_token = csrf_data.get("query", {}).get("tokens", {}).get("csrftoken")
    if csrf_token is None:
        logger.error(f"CSRF token not found in response: {csrf_data}")
        return json.dumps({"error": "get_csrf_token failed", "csrftoken_data": csrf_data})

    api_params["token"] = csrf_token
    api_params["format"] = "json"

    logger.debug(f"post_params: apiParams: {api_params}")

    client = get_oauth_client(access_key, access_secret, https_domain.replace("https://", ""))
    response = requests.post(api_url, data=api_params, auth=client, timeout=60)
    return response.text


def get_cxtoken(wiki: str, access_key: str, access_secret: str) -> dict[str, Any]:
    """Get CX token for Content Translation.

    Args:
        wiki: Wiki domain (e.g., 'en')
        access_key: OAuth access key
        access_secret: OAuth access secret

    Returns:
        API response as dictionary
    """
    https_domain = f"https://{wiki}.wikipedia.org"
    api_params = {
        "action": "cxtoken",
    }

    response = post_params(api_params, https_domain, access_key, access_secret)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse cxtoken response: {response}")
        result = {"error": "Failed to parse response"}

    if result is None or "error" in result:
        logger.error(f"get_cxtoken error: {result}")

    return result or {}
