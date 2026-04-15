"""
Tests for cors wrappers module, to test response.headers["Access-Control-Allow-Origin"] value
"""

from unittest.mock import MagicMock

import pytest

from src.app_main.cors import validate_access, check_cors


@validate_access
def wrap_validate_access(_mock) -> MagicMock:
    _mock = MagicMock()
    _mock.headers = {}
    return _mock


@check_cors
def wrap_check_cors(_mock) -> MagicMock:
    _mock = MagicMock()
    _mock.headers = {}
    return _mock


class TestValidateAccessControlAllowOrigin:
    ...


class TestCheckCorsAccessControlAllowOrigin:
    ...
