"""Application configuration helpers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .classes import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
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
    return Settings.load()


# Singleton settings instance
settings = get_settings()


def ensure_directories() -> None:
    """Create application directories if they don't exist.

    Call this once at app startup (in the factory), not at import time.
    """
    for dir_name in [
        settings.paths.flask_data_dir,
        settings.paths.log_dir,
        settings.paths.publish_reports_dir,
    ]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    for file_name in [
        settings.paths.words_json_path,
        settings.paths.revids_file_path,
    ]:
        Path(file_name).parent.mkdir(parents=True, exist_ok=True)

    settings.new_html.revisions_dir.mkdir(parents=True, exist_ok=True)

    # Ensure JSON index files exist
    for json_path in (
        settings.new_html.json_file,
        settings.new_html.json_file_all,
    ):
        if not json_path.exists():
            json_path.write_text("{}", encoding="utf-8")


__all__ = [
    "ensure_directories",
    "settings",
]
