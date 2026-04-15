"""
Tests for cors wrappers module.
"""

from unittest.mock import MagicMock

import pytest

from src.app_main.cors import validate_access, check_cors


@pytest.fixture
def mock_is_allowed(mocker):
    return mocker.patch("src.app_main.cors.is_allowed", return_value=None)


@pytest.fixture
def mock_check_secret(mocker):
    return mocker.patch("src.app_main.cors.check_publish_secret_code", return_value=None)


@pytest.fixture
def mock_load_request(mocker):
    mock_req = MagicMock()
    mocker.patch("src.app_main.cors._load_request", return_value=mock_req)
    return mock_req


class TestValidateAccessDecorated:
    def test_allowed_domain_calls_wrapped_function(self, app, mock_load_request, mock_is_allowed, mock_check_secret):
        mock_is_allowed.return_value = "trusted.com"
        mock_func = MagicMock(return_value="ok")
        decorated = validate_access(mock_func)

        result = decorated()

        mock_func.assert_called_once()
        assert result == "ok"

    def test_valid_secret_code_calls_wrapped_function(self, app, mock_load_request, mock_is_allowed, mock_check_secret):
        mock_is_allowed.return_value = None
        mock_check_secret.return_value = "secret-host.com"
        mock_func = MagicMock(return_value="ok")
        decorated = validate_access(mock_func)

        result = decorated()

        mock_func.assert_called_once()
        assert result == "ok"

    def test_both_valid_calls_wrapped_function(self, app, mock_load_request, mock_is_allowed, mock_check_secret):
        mock_is_allowed.return_value = "trusted.com"
        mock_check_secret.return_value = "secret-host.com"
        mock_func = MagicMock(return_value="ok")
        decorated = validate_access(mock_func)

        result = decorated()

        mock_func.assert_called_once()

    def test_neither_valid_returns_403(self, app, mock_load_request, mock_is_allowed, mock_check_secret):
        mock_is_allowed.return_value = None
        mock_check_secret.return_value = None
        mock_func = MagicMock()
        decorated = validate_access(mock_func)

        result = decorated()

        mock_func.assert_not_called()
        assert result.status_code == 403

    def test_neither_valid_returns_secret_key_error(self, app, mock_load_request, mock_is_allowed, mock_check_secret):
        mock_is_allowed.return_value = None
        mock_check_secret.return_value = None
        decorated = validate_access(lambda: "ok")

        result = decorated()
        data = result.get_json()

        assert data["error"]["code"] == "access_denied"
        assert "secret key" in data["error"]["info"].lower()

    def test_passes_args_and_kwargs(self, app, mock_load_request, mock_is_allowed, mock_check_secret):
        mock_is_allowed.return_value = "trusted.com"
        mock_func = MagicMock(return_value="result")
        decorated = validate_access(mock_func)

        decorated("arg1", key="value")

        mock_func.assert_called_once_with("arg1", key="value")

    def test_preserves_function_metadata(self, app, mock_load_request, mock_is_allowed, mock_check_secret):
        mock_is_allowed.return_value = "trusted.com"

        def my_func():
            """My docstring."""
            pass

        decorated = validate_access(my_func)
        assert decorated.__name__ == "my_func"
        assert decorated.__doc__ == "My docstring."


class TestCheckCorsAccessDecorated:
    def test_allowed_domain_calls_wrapped_function(self, app, mock_load_request, mock_is_allowed):
        mock_is_allowed.return_value = "trusted.com"
        mock_func = MagicMock(return_value="ok")
        decorated = check_cors(mock_func)

        result = decorated()

        mock_func.assert_called_once()
        assert result == "ok"

    def test_denied_returns_403(self, app, mock_load_request, mock_is_allowed):
        mock_is_allowed.return_value = None
        mock_func = MagicMock()
        decorated = check_cors(mock_func)

        result = decorated()

        mock_func.assert_not_called()
        assert result.status_code == 403

    def test_denied_returns_domain_error(self, app, mock_load_request, mock_is_allowed):
        mock_is_allowed.return_value = None
        decorated = check_cors(lambda: "ok")

        result = decorated()
        data = result.get_json()

        assert data["error"]["code"] == "access_denied"
        assert "authorized domains" in data["error"]["info"]

    def test_passes_args_and_kwargs(self, app, mock_load_request, mock_is_allowed):
        mock_is_allowed.return_value = "trusted.com"
        mock_func = MagicMock(return_value="result")
        decorated = check_cors(mock_func)

        decorated("arg1", key="value")

        mock_func.assert_called_once_with("arg1", key="value")

    def test_preserves_function_metadata(self, app, mock_load_request, mock_is_allowed):
        mock_is_allowed.return_value = "trusted.com"

        def my_func():
            """My docstring."""
            pass

        decorated = check_cors(my_func)
        assert decorated.__name__ == "my_func"
        assert decorated.__doc__ == "My docstring."
