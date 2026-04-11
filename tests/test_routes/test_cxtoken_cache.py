"""
Tests for app_routes.cxtoken.cache module.
"""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from src.app_main.app_routes.cxtoken.cache import CxToken, store_jwt, get_from_store
from tests.conftest import create_app
