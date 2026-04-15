import functools

from flask import jsonify, request
from flask.wrappers import Request

from .is_allowed_checker import is_allowed
from .publish_secret_checks import check_publish_secret_code


def _load_request() -> Request:
    return request


def validate_access(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request = _load_request()
        allowed = is_allowed(request)
        has_valid_secret_code = check_publish_secret_code()

        if has_valid_secret_code or allowed:
            response = func(*args, **kwargs)

            if hasattr(response, "headers"):
                response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"

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
            response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"

        return response

    return wrapper


__all__ = [
    "is_allowed",
    "check_publish_secret_code",
    "validate_access",
    "check_cors",
]
