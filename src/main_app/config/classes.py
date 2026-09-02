"""Application configuration helpers."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# --- Helper Functions ---


def _env_bool(name: str, default: bool = False) -> bool:
    """Convert environment variable to boolean."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, safe: bool = False) -> int:
    """Convert environment variable to integer."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:  # pragma: no cover - defensive guard
        if not safe:
            raise ValueError(f"Environment variable {name} must be an integer") from exc
        else:
            return default


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


def resolve_path(_path) -> Path:
    """Expand environment variables and user home directory in paths."""
    _path = os.path.expandvars(str(_path))
    _path = Path(_path).expanduser()
    return _path


# --- Data Classes for Configuration Sections ---


@dataclass(frozen=True)
class NewHtmlConfig:
    """
    Configuration for the new_html blueprint.
    Handles revision cache path and external API endpoints.
    """

    revisions_dir: Path
    transform_base_url: str = "https://en.wikipedia.org/w/rest.php/v1"
    segment_api_as_json: bool = True

    @property
    def json_file(self) -> Path:
        """Path to the main title → revision index."""
        return self.revisions_dir / "json_data.json"

    @property
    def json_file_all(self) -> Path:
        """Path to the 'all' / Video pages title → revision index."""
        return self.revisions_dir / "json_data_all.json"

    @classmethod
    def load(cls) -> NewHtmlConfig:
        """
        Load configuration for the new_html blueprint.
        """
        revisions_dir = Path(
            os.getenv(
                "REVISIONS_DIR",
                Path.home() / "public_html" / "revisions_new1",
            )
        )

        return NewHtmlConfig(
            revisions_dir=revisions_dir,
            transform_base_url=os.getenv(
                "TRANSFORM_BASE_URL",
                "https://en.wikipedia.org/w/rest.php/v1",
            ),
            segment_api_as_json=os.getenv("SEGMENT_API_AS_JSON", "true").lower() in ("1", "true", "yes"),
        )


@dataclass(frozen=True)
class OtherConfig:
    """configs not in specific sections"""

    csrf_time_limit: int | None  # None means never expire
    user_agent: str
    wiki_domain: str
    static_server: str
    tool_title: str
    revids_api_url: str
    wikidata_domain: str

    @classmethod
    def load(cls) -> OtherConfig:
        # CSRF token lifetime (in seconds). Default 3600 (1 hour).
        # Set to 0 or None to disable expiration (not recommended for production).
        csrf_time_limit = _env_int("WTF_CSRF_TIME_LIMIT", 3600)
        if not csrf_time_limit or csrf_time_limit <= 0:
            csrf_time_limit = 3600

        wiki_domain = os.getenv("WIKI_DOMAIN") or "commons.wikimedia.org"
        static_server = os.getenv("STATIC_SERVER") or "https://tools-static.wmflabs.org/cdnjs"

        user_agent = os.getenv(
            "USER_AGENT",
            "mdwikipy/1.0 (https://mdwikipy.toolforge.org; tools.mdwikipy@toolforge.org)",
        )
        revids_api_url = os.getenv("REVIDS_API_URL") or "https://mdwiki.toolforge.org/api.php"
        wikidata_domain = os.getenv("WIKIDATA_DOMAIN") or "www.wikidata.org"

        tool_title = os.getenv("TOOL_TITLE") or "mdwikipy tools"

        return OtherConfig(
            csrf_time_limit=csrf_time_limit,
            user_agent=user_agent,
            wiki_domain=wiki_domain,
            static_server=static_server,
            tool_title=tool_title,
            revids_api_url=revids_api_url,
            wikidata_domain=wikidata_domain,
        )


@dataclass(frozen=True)
class DbConfig:
    db_name: str
    db_host: str
    db_user: str | None
    db_password: str | None

    def to_json(self) -> dict[str, Any]:
        return {
            "db_name": self.db_name,
            "db_host": self.db_host,
            "db_user": self.db_user,
            "db_password": self.db_password,
        }

    @classmethod
    def load(cls) -> DbConfig:
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


@dataclass(frozen=True)
class Paths:
    flask_data_dir: Path
    log_dir: Path
    publish_reports_dir: Path
    words_json_path: Path
    revids_file_path: Path

    @classmethod
    def load(cls) -> Paths:
        flask_data_dir = os.getenv("MAIN_DIR") or "~/data"
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

    def all_paths(self) -> list[Path]:
        return [
            self.flask_data_dir,
            self.log_dir,
            self.publish_reports_dir,
        ]


@dataclass(frozen=True)
class CookieConfig:
    name: str
    max_age: int
    secure: bool
    httponly: bool
    samesite: str

    @classmethod
    def load(cls) -> CookieConfig:
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


@dataclass(frozen=True)
class SessionConfig:
    """Keys used for storing data in Flask session."""

    state_key: str
    request_token_key: str
    request_secret_key: str

    @classmethod
    def load(cls) -> SessionConfig:
        return cls(
            state_key=os.getenv("STATE_SESSION_KEY", "oauth_state_nonce"),
            request_token_key=os.getenv("REQUEST_TOKEN_SESSION_KEY", "state"),
            request_secret_key=os.getenv("REQUEST_SECRET_SESSION_KEY", "oauth_request_secret"),
        )


@dataclass(frozen=True)
class OAuthConfig:
    """MediaWiki OAuth specific configuration."""

    mw_uri: str
    consumer_key: str
    consumer_secret: str
    encryption_key: str | None

    @classmethod
    def load(cls) -> OAuthConfig:
        """
        Loads OAuth settings and validates them if enabled.

        Raises:
            RuntimeError: If OAUTH_ENCRYPTION_KEY is missing.
        """
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
            raise RuntimeError("OAUTH_ENCRYPTION_KEY environment variable is required")

        return OAuthConfig(
            mw_uri=mw_uri,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            encryption_key=encryption_key,
        )


@dataclass(frozen=True)
class CorsConfig:
    allowed_domains: list[str]

    @classmethod
    def load(cls) -> CorsConfig:
        # Load CORS configuration
        cors_domains_str = os.getenv("CORS_ALLOWED_DOMAINS", "medwiki.toolforge.org,mdwikicx.toolforge.org")
        cors_domains = [d.strip() for d in cors_domains_str.split(",") if d.strip()]

        return CorsConfig(
            allowed_domains=cors_domains,
        )


@dataclass(frozen=True)
class UsersConfig:
    """Configuration for user-related settings."""

    special_users: dict[str, str]  # Maps alternate usernames to canonical usernames
    fallback_user: str  # Fallback user for retry operations
    users_without_hashtag: tuple[str, ...]  # Users who don't get hashtags on their own pages

    @classmethod
    def load(cls) -> UsersConfig:
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

        return users_config


@dataclass(frozen=True)
class SecurityConfig:
    """Security configuration for Flask 3.1+ features."""

    secret_key: str
    salt: str
    max_content_length: int  # Maximum request size in bytes
    max_form_memory_size: int  # Maximum form data in memory in bytes
    max_form_parts: int  # Maximum number of form fields
    secret_key_fallbacks: tuple[str, ...]  # Fallback secret keys for rotation
    publish_secret_code: str

    @classmethod
    def load(cls) -> SecurityConfig:
        """
        Load security configuration (Flask 3.1+ features)
        """
        # MAX_CONTENT_LENGTH: Maximum request size (default 16MB)
        max_content_length = _env_int("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)

        # MAX_FORM_MEMORY_SIZE: Maximum form data in memory (default 16MB)
        max_form_memory_size = _env_int("MAX_FORM_MEMORY_SIZE", 16 * 1024 * 1024)

        # MAX_FORM_PARTS: Maximum number of form fields (default 1000)
        max_form_parts = _env_int("MAX_FORM_PARTS", 1000)

        # SECRET_KEY_FALLBACKS: Comma-separated list of fallback secret keys for rotation
        secret_key_fallbacks_str = os.getenv("SECRET_KEY_FALLBACKS", "")
        secret_key_fallbacks = tuple(key.strip() for key in secret_key_fallbacks_str.split(",") if key.strip())

        secret_key = os.getenv("FLASK_SECRET_KEY", "")
        secret_salt = os.getenv("SECRET_SALT", "mdwikipy")

        publish_secret_code = os.getenv("PUBLISH_SECRET_CODE", "")

        security_config = SecurityConfig(
            salt=secret_salt,
            secret_key=secret_key,
            max_content_length=max_content_length,
            max_form_memory_size=max_form_memory_size,
            max_form_parts=max_form_parts,
            secret_key_fallbacks=secret_key_fallbacks,
            publish_secret_code=publish_secret_code,
        )

        if not security_config.secret_key:
            raise RuntimeError("FLASK_SECRET_KEY environment variable is required")

        return security_config


@dataclass(frozen=True)
class Settings:
    """Main settings container."""

    # Nested configurations
    database_data: DbConfig
    paths: Paths
    cookie: CookieConfig
    sessions: SessionConfig
    oauth: OAuthConfig
    security: SecurityConfig
    other: OtherConfig
    users: UsersConfig
    cors: CorsConfig
    new_html: NewHtmlConfig

    @classmethod
    def load(cls) -> Settings:
        """
        Initialize and return a cached Settings object.
        Main entry point for application configuration.

        Returns:
            Settings: The populated application settings.

        Raises:
            RuntimeError: If FLASK_SECRET_KEY is not set.
            RuntimeError: If OAUTH_ENCRYPTION_KEY is missing.
            RuntimeError: If the OAuth configuration (OAUTH_MWURI, OAUTH_CONSUMER_KEY, OAUTH_CONSUMER_SECRET) is incomplete.
        """
        return Settings(
            security=SecurityConfig.load(),
            paths=Paths.load(),
            database_data=DbConfig.load(),
            cookie=CookieConfig.load(),
            oauth=OAuthConfig.load(),
            sessions=SessionConfig.load(),
            other=OtherConfig.load(),
            cors=CorsConfig.load(),
            users=UsersConfig.load(),
            new_html=NewHtmlConfig.load(),
        )


__all__ = [
    "DbConfig",
    "Paths",
    "CookieConfig",
    "SessionConfig",
    "OAuthConfig",
    "Settings",
    "OtherConfig",
    "SecurityConfig",
    "CorsConfig",
    "UsersConfig",
]
