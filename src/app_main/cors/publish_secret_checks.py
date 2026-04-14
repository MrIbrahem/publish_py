"""

"""
import hmac
import logging
from urllib.parse import urlparse
from flask import request

from ..config import settings

logger = logging.getLogger(__name__)


def check_publish_secret_code() -> str | None:
    expected_secret = settings.publish_secret_code
    if not expected_secret:
        return None

    received_secret = request.headers.get("X-Secret-Key")

    if not received_secret or not hmac.compare_digest(received_secret, expected_secret):
        return None

    host = request.headers.get("Origin") or request.host_url

    return urlparse(host).netloc
