"""
Integration tests for src/sqlalchemy_app/public/routes/api/routes.py module.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask.app import Flask
from flask.testing import FlaskClient
