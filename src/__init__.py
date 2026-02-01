try:
    from env_config import _env_file_path  # noqa: F401 # Triggers environment configuration
except ImportError:
    from .env_config import _env_file_path  # noqa: F401 # Triggers environment configuration
