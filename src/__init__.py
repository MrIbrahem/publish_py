"""
Source package initialization.
Loads environment configuration on import for backward compatibility.
"""

try:
    from env_config import load_environment

    load_environment()
except ImportError:
    from .env_config import load_environment

    load_environment()
