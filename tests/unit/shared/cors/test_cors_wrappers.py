"""
Tests for cors wrappers module.
"""

from unittest.mock import MagicMock

from src.app_main.shared.cors import check_cors, validate_access


class TestValidateAccessDecorated:
    def test_allowed_domain_calls_wrapped_function(self, app, mock_load_request, mock_is_allowed, mock_check_secret):
        mock_is_allowed.return_value = "trusted.com"
        mock_func = MagicMock(return_value="ok")
        decorated = validate_access(mock_func)

        result = decorated()

        mock_func.assert_called_once()
        assert result == "ok"

    def test_valid_secret_code_calls_wrapped_function(self, app, mock_load_request, mock_is_denied, mock_check_secret):

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
        assert result == "ok"

    def test_neither_valid_returns_403(self, app, mock_load_request, mock_is_denied, mock_check_secret):

        mock_check_secret.return_value = None
        mock_func = MagicMock()
        decorated = validate_access(mock_func)

        result = decorated()

        mock_func.assert_not_called()
        assert result.status_code == 403

    def test_neither_valid_returns_secret_key_error(self, app, mock_load_request, mock_is_denied, mock_check_secret):

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

    def test_denied_returns_403(self, app, mock_load_request, mock_is_denied):

        mock_func = MagicMock()
        decorated = check_cors(mock_func)

        result = decorated()

        mock_func.assert_not_called()
        assert result.status_code == 403

    def test_denied_returns_domain_error(self, app, mock_load_request, mock_is_denied):

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
