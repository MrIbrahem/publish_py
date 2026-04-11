"""Application configuration helpers."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class DbConfig:
    db_name: str
    db_host: str
    db_user: str | None
    db_password: str | None


@dataclass(frozen=True)
class Paths:
    flask_data_dir: str
    log_dir: str
    publish_reports_dir: str
    words_json_path: str
    revids_file_path: Path


@dataclass(frozen=True)
class CookieConfig:
    name: str
    max_age: int
    secure: bool
    httponly: bool
    samesite: str


@dataclass(frozen=True)
class OAuthConfig:
    mw_uri: str
    consumer_key: str
    consumer_secret: str
    user_agent: str


@dataclass(frozen=True)
class CorsConfig:
    allowed_domains: tuple[str, ...]


@dataclass(frozen=True)
class UsersConfig:
    """Configuration for user-related settings."""

    special_users: dict[str, str]  # Maps alternate usernames to canonical usernames
    fallback_user: str  # Fallback user for retry operations
    users_without_hashtag: tuple[str, ...]  # Users who don't get hashtags on their own pages


@dataclass(frozen=True)
class Settings:
    is_localhost: Callable[[str], bool]
    database_data: DbConfig
    STATE_SESSION_KEY: str
    REQUEST_TOKEN_SESSION_KEY: str
    secret_key: str
    use_mw_oauth: bool
    oauth_encryption_key: Optional[str]
    cookie: CookieConfig
    oauth: Optional[OAuthConfig]
    paths: Paths
    cors: CorsConfig
    users: UsersConfig


def _load_database_credentials() -> DbConfig:
    TOOL_TOOLSDB_HOST = os.getenv("TOOL_TOOLSDB_HOST", "")

    data = DbConfig(
        db_name=os.getenv("TOOL_TOOLSDB_DBNAME", ""),
        db_host=TOOL_TOOLSDB_HOST,
        db_user=os.getenv("TOOL_TOOLSDB_USER", None),
        db_password=os.getenv("TOOL_TOOLSDB_PASSWORD", None),
    )
    return data


def resolve_path(_path) -> Path:
    _path = os.path.expandvars(str(_path))
    _path = Path(_path).expanduser()
    return _path


def _get_paths() -> Paths:
    flask_data_dir = os.getenv("FLASK_DATA_DIR") or os.path.join(os.path.expanduser("~"), "~/data")
    log_dir = f"{flask_data_dir}/logs"
    publish_reports_dir = os.getenv("PUBLISH_REPORTS_DIR") or f"{flask_data_dir}/publish_reports/reports_by_day"
    words_json_path = os.getenv("WORDS_JSON_PATH") or f"{flask_data_dir}/td/Tables/jsons/words.json"

    revids_file_path = os.getenv("ALL_PAGES_REVIDS_PATH") or "~/public_html/all_pages_revids.json"

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    return Paths(
        flask_data_dir=flask_data_dir,
        log_dir=log_dir,
        publish_reports_dir=publish_reports_dir,
        words_json_path=words_json_path,
        revids_file_path=resolve_path(revids_file_path),
    )


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Environment variable {name} must be an integer") from exc


def _load_oauth_config() -> Optional[OAuthConfig]:
    mw_uri = os.getenv("OAUTH_MWURI", "")
    consumer_key = os.getenv("OAUTH_CONSUMER_KEY", "")
    consumer_secret = os.getenv("OAUTH_CONSUMER_SECRET", "")
    if not (mw_uri and consumer_key and consumer_secret):
        return None

    return OAuthConfig(
        mw_uri=mw_uri,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        user_agent=os.getenv(
            "USER_AGENT",
            "mdwikipy/1.0 (https://mdwikipy.toolforge.org; tools.mdwikipy@toolforge.org)",
        ),
    )


def is_localhost(host: str) -> bool:
    local_hosts = [
        "localhost",
        "127.0.0.1",
    ]

    return any(x in host for x in local_hosts)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    secret_key = os.getenv("FLASK_SECRET_KEY", "")
    if not secret_key:
        raise RuntimeError("FLASK_SECRET_KEY environment variable is required")

    session_cookie_secure = _env_bool("SESSION_COOKIE_SECURE", default=True)
    session_cookie_httponly = _env_bool("SESSION_COOKIE_HTTPONLY", default=True)
    session_cookie_samesite = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    STATE_SESSION_KEY = os.getenv("STATE_SESSION_KEY", "oauth_state_nonce")
    REQUEST_TOKEN_SESSION_KEY = os.getenv("REQUEST_TOKEN_SESSION_KEY", "state")

    use_mw_oauth = _env_bool("USE_MW_OAUTH", default=True)
    oauth_config = _load_oauth_config()

    oauth_encryption_key = os.getenv("OAUTH_ENCRYPTION_KEY", "")
    if use_mw_oauth and not oauth_encryption_key:
        raise RuntimeError("OAUTH_ENCRYPTION_KEY environment variable is required when USE_MW_OAUTH is enabled")

    cookie = CookieConfig(
        name=os.getenv("AUTH_COOKIE_NAME", "uid_enc"),
        max_age=_env_int("AUTH_COOKIE_MAX_AGE", 30 * 24 * 3600),
        secure=session_cookie_secure,
        httponly=session_cookie_httponly,
        samesite=session_cookie_samesite,
    )

    # Load CORS configuration
    cors_domains_str = os.getenv("CORS_ALLOWED_DOMAINS", "medwiki.toolforge.org,mdwikicx.toolforge.org")
    cors_domains = tuple(d.strip() for d in cors_domains_str.split(",") if d.strip())
    cors_config = CorsConfig(allowed_domains=cors_domains)

    # Load users configuration
    # Special users mapping: comma-separated pairs of "alternate:canonical"
    special_users_str = os.getenv("SPECIAL_USERS", "Mr. Ibrahem 1:Mr. Ibrahem,Admin:Mr. Ibrahem")
    special_users = {}
    for pair in special_users_str.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if ":" not in pair:
            # Log warning for malformed pair (missing colon)
            import logging

            logging.getLogger(__name__).warning(f"Ignoring malformed SPECIAL_USERS pair (missing ':'): {pair}")
            continue
        alt, canonical = pair.split(":", 1)
        special_users[alt.strip()] = canonical.strip()

    fallback_user = os.getenv("FALLBACK_USER", "Mr. Ibrahem")

    users_without_hashtag_str = os.getenv("USERS_WITHOUT_HASHTAG", "Mr. Ibrahem")
    users_without_hashtag = tuple(u.strip() for u in users_without_hashtag_str.split(",") if u.strip())

    users_config = UsersConfig(
        special_users=special_users,
        fallback_user=fallback_user,
        users_without_hashtag=users_without_hashtag,
    )

    if use_mw_oauth and oauth_config is None:
        raise RuntimeError(
            "MediaWiki OAuth configuration is incomplete. Set OAUTH_MWURI, OAUTH_CONSUMER_KEY, and OAUTH_CONSUMER_SECRET."
        )

    return Settings(
        is_localhost=is_localhost,
        paths=_get_paths(),
        database_data=_load_database_credentials(),
        STATE_SESSION_KEY=STATE_SESSION_KEY,
        REQUEST_TOKEN_SESSION_KEY=REQUEST_TOKEN_SESSION_KEY,
        secret_key=secret_key,
        use_mw_oauth=use_mw_oauth,
        oauth_encryption_key=oauth_encryption_key,
        cookie=cookie,
        oauth=oauth_config,
        cors=cors_config,
        users=users_config,
    )


settings = get_settings()


# =============================================================================
# Flask-style Configuration Classes
# =============================================================================
# These classes follow Flask's conventional configuration pattern and are
# designed to work with create_app(config_class=ConfigClass).
#
# Example usage:
#     from app_main import create_app
#     from app_main.config import TestingConfig
#     app = create_app(TestingConfig)
# =============================================================================


class Config:
    """Base configuration class for Flask applications.

    This class provides Flask-standard configuration attributes that can be
    used with app.config.from_object(). It wraps the dataclass-based settings.
    """

    # Flask core settings
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: str | None = None
    SECRET_KEY_FALLBACKS: list[str] | None = None

    # Session cookie settings (populated from settings by default)
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"

    # CSRF protection settings
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_TIME_LIMIT: int | None = None  # None = tokens don't expire
    WTF_CSRF_SSL_STRICT: bool = True

    # Request handling
    MAX_CONTENT_LENGTH: int | None = 16 * 1024 * 1024  # 16MB default

    def __init__(self) -> None:
        """Initialize configuration with values from environment-based settings."""
        # Sync with the dataclass-based settings for backward compatibility
        self.SECRET_KEY = settings.secret_key
        self.SESSION_COOKIE_HTTPONLY = settings.cookie.httponly
        self.SESSION_COOKIE_SECURE = settings.cookie.secure
        self.SESSION_COOKIE_SAMESITE = settings.cookie.samesite

        # Load SECRET_KEY_FALLBACKS from environment for key rotation support
        # Format: comma-separated list of fallback keys
        # Example: FLASK_SECRET_KEY_FALLBACKS="old-key-1,old-key-2"
        fallbacks_str = os.getenv("FLASK_SECRET_KEY_FALLBACKS", "")
        if fallbacks_str:
            self.SECRET_KEY_FALLBACKS = [key.strip() for key in fallbacks_str.split(",") if key.strip()]


class DevelopmentConfig(Config):
    """Development configuration with debugging enabled."""

    DEBUG: bool = True
    SESSION_COOKIE_SECURE: bool = False  # Allow HTTP in development
    WTF_CSRF_SSL_STRICT: bool = False  # Allow CSRF without HTTPS


class TestingConfig(Config):
    """Testing configuration with CSRF disabled for easier form testing."""

    # Prevent pytest from collecting this as a test class
    __test__ = False

    DEBUG: bool = False
    TESTING: bool = True
    WTF_CSRF_ENABLED: bool = False  # Disable CSRF for test requests
    SESSION_COOKIE_SECURE: bool = False

    # Use a fixed test secret key
    SECRET_KEY: str = "test-secret-key-not-for-production"


class ProductionConfig(Config):
    """Production configuration with strict security settings."""

    DEBUG: bool = False
    TESTING: bool = False
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_SSL_STRICT: bool = True

    # Production should always use secure cookies
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
