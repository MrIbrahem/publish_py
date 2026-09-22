from __future__ import annotations

import logging
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
            logger.warning("Environment already initialized")
            return

        cls._load_environment(env_path)
        cls._setup_fix_refs_path()
        cls._setup_html_to_segments_path()
        cls._initialized = True

    @staticmethod
    def _load_environment(env_path: Path | str | None = None) -> None:
        """Locate and load the .env file into os.environ."""
        if env_path is None:
            # Default location: 3 levels up from this file or root directory
            env_path = Path(__file__).resolve().parent.parent.parent / ".env"
            logger.warning("No .env file specified, using default path: %s", env_path)
        else:
            env_path = Path(env_path)

        try:
            if env_path.is_file():
                load_dotenv(dotenv_path=env_path)
            else:
                logger.warning("Environment file not found at: %s", env_path)
        except Exception as exc:
            logger.warning("Failed to load .env file from %s: %s", env_path, exc)

    @staticmethod
    def _setup_fix_refs_path() -> None:
        """Check for fix_refs availability and dynamically append its path if configured."""
        try:
            from fix_refs import fix_one_page  # noqa: F401
        except ImportError:
            logger.warning("fix_refs library not found")
            msg = """
            Please install fix_refs from https://github.com/MrIbrahem/fix_refs_new_py
                - `pip install git+https://github.com/MrIbrahem/fix_refs_new_py.git -U`
            or clone fix_refs into your workspace and inside `fix_refs_new_py` folder run:
                - `pip install -e .`
            """
            logger.error(msg)

    @staticmethod
    def _setup_html_to_segments_path() -> None:
        """Check for html_to_segments availability and dynamically append its path if configured."""
        try:
            from html_to_segments import process_html  # noqa: F401
        except ImportError:
            logger.warning("html_to_segments library not found")
            msg = """
            Please install html_to_segments from https://github.com/MrIbrahem/html_to_segments
                - `pip install git+https://github.com/MrIbrahem/html_to_segments.git -U`
            or clone html_to_segments into your workspace and inside `html_to_segments` folder run:
                - `pip install -e .`
            """
            logger.error(msg)


def init_app_environment(env_path: Path | str | None = None) -> None:
    """Helper function to trigger environment initialization."""
    EnvironmentInitializer.setup(env_path)
