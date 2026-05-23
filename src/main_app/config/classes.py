"""Application configuration helpers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# --- Data Classes for Configuration Sections ---


@dataclass(frozen=True)
class DbConfig:
    db_name: str
    db_host: str
    db_user: str | None
    db_password: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "db_name": self.db_name,
            "db_host": self.db_host,
            "db_user": self.db_user,
            "db_password": self.db_password,
        }


@dataclass(frozen=True)
class Paths:
    flask_data_dir: Path
    log_dir: Path
    publish_reports_dir: Path
    words_json_path: Path
    revids_file_path: Path


@dataclass(frozen=True)
class CookieConfig:
    name: str
    max_age: int
    secure: bool
    httponly: bool
    samesite: str


@dataclass(frozen=True)
class SessionConfig:
    """Keys used for storing data in Flask session."""

    state_key: str
    request_token_key: str


@dataclass(frozen=True)
class OAuthConfig:
    """MediaWiki OAuth specific configuration."""

    mw_uri: str
    consumer_key: str
    consumer_secret: str
    encryption_key: Optional[str]
    enabled: bool = True


@dataclass(frozen=True)
class CorsConfig:
    allowed_domains: list[str]


@dataclass(frozen=True)
class UsersConfig:
    """Configuration for user-related settings."""

    special_users: dict[str, str]  # Maps alternate usernames to canonical usernames
    fallback_user: str  # Fallback user for retry operations
    users_without_hashtag: tuple[str, ...]  # Users who don't get hashtags on their own pages


@dataclass(frozen=True)
class Settings:
    """Main settings container."""

    publish_secret_code: str
    secret_key: str
    user_agent: str
    revids_api_url: str
    wikidata_domain: str
    is_localhost: Callable[[str], bool]
    # has_db_config: callable

    # Nested configurations
    database_data: DbConfig
    paths: Paths
    cookie: CookieConfig
    sessions: SessionConfig
    oauth: Optional[OAuthConfig]
    cors: CorsConfig
    users: UsersConfig


__all__ = [
    "DbConfig",
    "Paths",
    "CookieConfig",
    "SessionConfig",
    "OAuthConfig",
    "CorsConfig",
    "UsersConfig",
    "Settings",
]
