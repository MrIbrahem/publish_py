"""Application configuration helpers."""

from __future__ import annotations

import os
from .config.main_settings import settings


def has_db_config() -> bool:
    """Return True when database connection details are configured."""
    return bool(settings.database_data.db_host)


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
    WTF_CSRF_CHECK_DEFAULT: bool = True  # default value
    WTF_CSRF_FIELD_NAME: str = "csrf_token"  # default value
    WTF_CSRF_HEADERS: list[str] = ["X-CSRFToken", "X-CSRF-Token"]  # default value
    WTF_CSRF_METHODS: list[str] = ["POST", "PUT", "PATCH", "DELETE"]  # default value
    # WTF_CSRF_SECRET_KEY: str = settings.secret_key # default value

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI: str | None = None
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {}

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

        # Only set DB URI and engine options if not already defined by subclass
        # (e.g., TestingConfig sets SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:")
        if self.SQLALCHEMY_DATABASE_URI is None:
            # Build SQLAlchemy database URI from environment config
            db_cfg = settings.database_data
            if db_cfg.db_host:
                from urllib.parse import quote_plus

                password = quote_plus(db_cfg.db_password or "")
                self.SQLALCHEMY_DATABASE_URI = (
                    f"mysql+pymysql://{db_cfg.db_user}:{password}"
                    f"@{db_cfg.db_host}/{db_cfg.db_name}"
                    f"?charset=utf8mb4"
                )

        # Only set MySQL-specific engine options if URI is MySQL (not SQLite)
        uri = self.SQLALCHEMY_DATABASE_URI or ""
        if uri.startswith("mysql") and not self.SQLALCHEMY_ENGINE_OPTIONS:
            self.SQLALCHEMY_ENGINE_OPTIONS = {
                "pool_pre_ping": True,
                "pool_size": 5,
                "max_overflow": 10,
                "pool_recycle": 3600,
                "connect_args": {
                    "connect_timeout": 5,
                    "init_command": 'SET time_zone = "+00:00"',
                    "charset": "utf8mb4",
                    "collation": "utf8mb4_unicode_ci",
                },
            }


class DevelopmentConfig(Config):
    """Development configuration with debugging enabled."""

    DEBUG: bool = True
    TESTING: bool = True
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_SSL_STRICT: bool = True

    # Production should always use secure cookies
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"

    # Disable CORS for testing
    CORS_DISABLED: bool = True


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

    # Use SQLite in-memory for tests (no MySQL dependency)
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS: dict = {}  # SQLite doesn't need MySQL options

    # Disable CORS for testing
    CORS_DISABLED: bool = True


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

    CORS_DISABLED: bool = False
