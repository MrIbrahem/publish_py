from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class EnvironmentInitializer:
    """Handles environment variable loading and dynamic path registrations."""

    _initialized: bool = False

    @classmethod
    def setup(cls, env_path: Path | str | None = None) -> None:
        """
        Load environment variables and inject required dynamic module paths.
        Ensures execution happens only once per runtime.
        """
        if cls._initialized:
            return

        cls._load_environment(env_path)
        cls._setup_fix_refs_path()
        cls._initialized = True

    @staticmethod
    def _load_environment(env_path: Path | str | None = None) -> None:
        """Locate and load the .env file into os.environ."""
        if env_path is None:
            # Default location: 3 levels up from this file or root directory
            env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        else:
            env_path = Path(env_path)

        try:
            if env_path.is_file():
                load_dotenv(dotenv_path=env_path)
            else:
                logger.warning("Environment file not found at: %s", env_path)
        except Exception as exc:
            logger.warning("Failed to load .env file from %s: %s", env_path, exc)

    @classmethod
    def _setup_fix_refs_path(cls, retry: bool = True) -> None:
        """Check for fix_refs availability and dynamically append its path if configured."""
        try:
            import fix_refs  # noqa: F401
            return None
        except ImportError:
            if not retry:
                logger.warning("fix_refs not found")
                return None

        fix_refs_path = os.getenv("FIX_REFS_PY_PATH", "")
        if not fix_refs_path or not os.path.isdir(fix_refs_path):
            return None

        if fix_refs_path not in sys.path:
            sys.path.insert(0, fix_refs_path)
            if retry:
                return cls._setup_fix_refs_path(retry=False)


def init_app_environment(env_path: Path | str | None = None) -> None:
    """Helper function to trigger environment initialization."""
    EnvironmentInitializer.setup(env_path)
