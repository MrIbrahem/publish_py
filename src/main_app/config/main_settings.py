"""Application configuration helpers."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from .classes import (
    DbConfig,
    Paths,
    CookieConfig,
    SessionConfig,
    OAuthConfig,
    CorsConfig,
    UsersConfig,
    Settings,
)


# --- Helper Functions ---


def _env_bool(name: str, default: bool = False) -> bool:
    """Convert environment variable to boolean."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    """Convert environment variable to integer."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Environment variable {name} must be an integer") from exc


def resolve_path(_path) -> Path:
    """Expand environment variables and user home directory in paths."""
    _path = os.path.expandvars(str(_path))
    _path = Path(_path).expanduser()
    return _path


# --- Configuration Loaders ---


def _load_database_config() -> DbConfig:
    """
    Construct a DbConfig populated from environment variables.

    Reads TOOL_TOOLSDB_DBNAME and TOOL_TOOLSDB_HOST (defaulting to empty string) and TOOL_TOOLSDB_USER and TOOL_TOOLSDB_PASSWORD (defaulting to None) and returns a DbConfig with those values.
    Returns:
        DbConfig: Configuration with fields:
            - db_name: from TOOL_TOOLSDB_DBNAME (default "").
            - db_host: from TOOL_TOOLSDB_HOST (default "").
            - db_user: from TOOL_TOOLSDB_USER (or None).
            - db_password: from TOOL_TOOLSDB_PASSWORD (or None).
    """
    return DbConfig(
        db_name=os.getenv("TOOL_TOOLSDB_DBNAME", ""),
        db_host=os.getenv("TOOL_TOOLSDB_HOST", ""),
        db_user=os.getenv("TOOL_TOOLSDB_USER", None),
        db_password=os.getenv("TOOL_TOOLSDB_PASSWORD", None),
    )


def _load_oauth_config() -> Optional[OAuthConfig]:
    """
    Loads OAuth settings and validates them if enabled.
    Returns None if USE_MW_OAUTH is disabled.
    """
    mw_oauth_enabled = _env_bool("USE_MW_OAUTH", default=True)
    if not mw_oauth_enabled:
        return None

    mw_uri = os.getenv("OAUTH_MWURI", "")
    consumer_key = os.getenv("OAUTH_CONSUMER_KEY", "")
    consumer_secret = os.getenv("OAUTH_CONSUMER_SECRET", "")
    encryption_key = os.getenv("OAUTH_ENCRYPTION_KEY", "")

    # Validate mandatory fields for OAuth
    if not all([mw_uri, consumer_key, consumer_secret]):
        raise RuntimeError(
            "MediaWiki OAuth configuration is incomplete. Set OAUTH_MWURI, OAUTH_CONSUMER_KEY, and OAUTH_CONSUMER_SECRET."
        )

    if not encryption_key:
        raise RuntimeError("OAUTH_ENCRYPTION_KEY is required when USE_MW_OAUTH is enabled")

    return OAuthConfig(
        mw_uri=mw_uri,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        encryption_key=encryption_key,
        enabled=mw_oauth_enabled,
    )


def _get_paths() -> Paths:
    flask_data_dir = os.getenv("FLASK_DATA_DIR") or "~/data"
    log_dir = f"{flask_data_dir}/logs"
    publish_reports_dir = os.getenv("PUBLISH_REPORTS_DIR") or f"{flask_data_dir}/publish_reports/reports_by_day"
    words_json_path = os.getenv("WORDS_JSON_PATH") or f"{flask_data_dir}/td/Tables/jsons/words.json"

    revids_file_path = os.getenv("ALL_PAGES_REVIDS_PATH") or "~/public_html/all_pages_revids.json"

    # Ensure log directory exists
    Path(resolve_path(log_dir)).mkdir(parents=True, exist_ok=True)

    return Paths(
        flask_data_dir=resolve_path(flask_data_dir),
        log_dir=resolve_path(log_dir),
        publish_reports_dir=resolve_path(publish_reports_dir),
        words_json_path=resolve_path(words_json_path),
        revids_file_path=resolve_path(revids_file_path),
    )


def is_localhost(host: str) -> bool:
    """Check if the host refers to a local environment."""
    local_hosts = [
        "localhost",
        "127.0.0.1",
    ]

    return any(x in host for x in local_hosts)


def load_cookie_config():
    session_cookie_secure = _env_bool("SESSION_COOKIE_SECURE", default=True)
    session_cookie_httponly = _env_bool("SESSION_COOKIE_HTTPONLY", default=True)
    session_cookie_samesite = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

    cookie = CookieConfig(
        name=os.getenv("AUTH_COOKIE_NAME", "uid_enc"),
        max_age=_env_int("AUTH_COOKIE_MAX_AGE", 30 * 24 * 3600),
        secure=session_cookie_secure,
        httponly=session_cookie_httponly,
        samesite=session_cookie_samesite,
    )

    return cookie


def load_special_users() -> dict:
    """
    Special users mapping: comma-separated pairs of "alternate:canonical"
    """
    special_users_str = os.getenv("SPECIAL_USERS", "Mr. Ibrahem 1:Mr. Ibrahem,Admin:Mr. Ibrahem")
    special_users = {}
    for pair in (p.strip() for p in special_users_str.split(",") if p.strip()):
        if ":" in pair:
            alt, canonical = pair.split(":", 1)
            special_users[alt.strip()] = canonical.strip()
        else:
            logging.getLogger(__name__).warning(f"Ignoring malformed SPECIAL_USERS pair (missing ':'): {pair}")

    return special_users


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Initialize and return a cached Settings object.
    Main entry point for application configuration.
    """
    secret_key = os.getenv("FLASK_SECRET_KEY", "")
    if not secret_key:
        raise RuntimeError("FLASK_SECRET_KEY environment variable is required")

    # Load and organize sub-configs
    cookie = load_cookie_config()

    sessions = SessionConfig(
        state_key=os.getenv("STATE_SESSION_KEY", "oauth_state_nonce"),
        request_token_key=os.getenv("REQUEST_TOKEN_SESSION_KEY", "state"),
    )

    # Load User Mappings
    special_users = load_special_users()
    fallback_user = os.getenv("FALLBACK_USER", "Mr. Ibrahem")

    users_without_hashtag_str = os.getenv("USERS_WITHOUT_HASHTAG") or "Mr. Ibrahem"
    users_without_hashtag = tuple(u.strip() for u in users_without_hashtag_str.split(",") if u.strip())

    users_config = UsersConfig(
        special_users=special_users,
        fallback_user=fallback_user,
        users_without_hashtag=users_without_hashtag,
    )

    # Load CORS configuration
    cors_domains_str = os.getenv("CORS_ALLOWED_DOMAINS", "medwiki.toolforge.org,mdwikicx.toolforge.org")
    cors_domains = [d.strip() for d in cors_domains_str.split(",") if d.strip()]

    cors_config = CorsConfig(allowed_domains=cors_domains)

    revids_api_url = os.getenv("REVIDS_API_URL") or "https://mdwiki.toolforge.org/api.php"
    wikidata_domain = os.getenv("WIKIDATA_DOMAIN") or "www.wikidata.org"

    user_agent = os.getenv("USER_AGENT", "mdwikipy/1.0 (https://mdwikipy.toolforge.org; tools.mdwikipy@toolforge.org)")
    publish_secret_code = os.getenv("PUBLISH_SECRET_CODE", "")

    return Settings(
        publish_secret_code=publish_secret_code,
        secret_key=secret_key,
        user_agent=user_agent,
        revids_api_url=revids_api_url,
        wikidata_domain=wikidata_domain,
        is_localhost=is_localhost,
        database_data=_load_database_config(),
        paths=_get_paths(),
        cookie=cookie,
        sessions=sessions,
        oauth=_load_oauth_config(),
        cors=cors_config,
        users=users_config,
    )


# Singleton settings instance
settings = get_settings()

__all__ = [
    "settings",
]
