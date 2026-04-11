"""Source package initialization.

Loads environment configuration on import for backward compatibility.
New code should explicitly call load_environment() from env_config.
"""

try:
    from env_config import load_environment

    load_environment()
except ImportError:
    from .env_config import load_environment

    load_environment()
