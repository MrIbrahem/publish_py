import functools
import validators
from urllib.parse import urlparse

from flask import jsonify, request
from flask.wrappers import Request

from .is_allowed_checker import is_allowed
from .publish_secret_checks import check_publish_secret_code


def _load_request() -> Request:
    return request


def is_domain(text: str):
    return validators.domain(text)


def _validate_url(text) -> str:
    if not text or not isinstance(text, str):
        return ""

    if not is_domain(text):
        return text

    # if text == "*" or text.startswith(("http://", "https://")):
    if text == "*" or urlparse(text).scheme:
        return text

    return f"https://{text}"


def validate_access(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request = _load_request()
        allowed = is_allowed(request)
        has_valid_secret_code = check_publish_secret_code()

        if has_valid_secret_code or allowed:
            response = func(*args, **kwargs)
            # uncomment next after testing TestValidateAccessControlAllowOrigin
            # allowed_url = has_valid_secret_code or allowed
            allowed_url = allowed

            if hasattr(response, "headers"):
                response.headers["Access-Control-Allow-Origin"] = _validate_url(allowed_url)

            return response

        if not has_valid_secret_code:
            response = jsonify({
                "error": {
                    "code": "access_denied",
                    "info": "Access denied. Invalid or missing secret key."
                }
            })
            response.status_code = 403
            return response

        response = jsonify({
            "error": {
                "code": "access_denied",
                "info": "Access denied. Requests are only allowed from authorized domains."
            }
        })
        response.status_code = 403
        return response

    return wrapper


def check_cors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request = _load_request()
        allowed = is_allowed(request)
        if not allowed:
            response = jsonify({
                "error": {
                    "code": "access_denied",
                    "info": "Access denied. Requests are only allowed from authorized domains."
                }
            })
            response.status_code = 403
            return response

        response = func(*args, **kwargs)
        if hasattr(response, "headers"):
            response.headers["Access-Control-Allow-Origin"] = _validate_url(allowed)

        return response

    return wrapper


__all__ = [
    "is_allowed",
    "check_publish_secret_code",
    "validate_access",
    "check_cors",
]
