import functools

from flask import jsonify, request

from .cors import is_allowed
from .publish_secret_checks import check_publish_secret_code


def validate_access(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        allowed = is_allowed(request)
        has_valid_secret_code = check_publish_secret_code()

        if has_valid_secret_code or allowed:
            response = func(*args, **kwargs)

            if hasattr(response, "headers"):
                response.headers["Access-Control-Allow-Origin"] = f"https://{allowed}"

            return response

        if not has_valid_secret_code:
            return jsonify({"error": "Access denied. Invalid or missing secret key."}), 403

        return jsonify({"error": "Access denied. Requests are only allowed from authorized domains."}), 403

    return wrapper


def check_cors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        allowed = is_allowed(request)
        if not allowed:
            return jsonify({"error": "Access denied. Requests are only allowed from authorized domains."}), 403

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
