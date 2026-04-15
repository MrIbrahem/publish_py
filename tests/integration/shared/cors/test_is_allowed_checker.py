"""
Tests for is_allowed — grouped by behavior branch.
"""

from typing import Any, Generator

import pytest
from flask import Flask


@pytest.fixture
def app() -> Generator[Flask, Any, None]:
    """Create a test Flask application."""
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config["TESTING"] = True
    app.config["CORS_DISABLED"] = False
    yield app


# ------------------------------------------------------------------
# 1. Same-Origin via Origin header
# ------------------------------------------------------------------


class TestSameOrigin:
    @pytest.mark.parametrize(
        "origin, expected",
        [
            # Origin matches server host exactly → return origin
            ("http://localhost/", "http://localhost"),
        ],
    )
    def test_origin_matches_server(self, app: Flask, origin, expected) -> None:
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(base_url=origin, headers={"Origin": origin.rstrip("/")}):
            from flask import request

            assert is_allowed(request) == expected

    def test_referer_matches_server(self, app: Flask) -> None:
        """Referer pointing to same server → return host_url stripped."""
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(base_url="http://localhost/", headers={"Referer": "http://localhost/some/page"}):
            from flask import request

            result = is_allowed(request)
            assert result == "http://localhost"

    def test_origin_and_referer_both_same_origin(self, app: Flask) -> None:
        """Both headers same-origin → still returns origin."""
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(
            base_url="http://localhost/", headers={"Origin": "http://localhost", "Referer": "http://localhost/page"}
        ):
            from flask import request

            result = is_allowed(request)
            assert result == "http://localhost"


# ------------------------------------------------------------------
# 2. Allowed domains list
# ------------------------------------------------------------------


class TestAllowedDomains:
    @pytest.mark.parametrize(
        "headers, expected",
        [
            # Origin exact match → returns domain string
            ({"Origin": "https://medwiki.toolforge.org"}, "https://medwiki.toolforge.org"),
            # Referer exact match (host extracted) → returns domain string
            ({"Referer": "https://mdwikicx.toolforge.org/page"}, "https://mdwikicx.toolforge.org"),
            # Origin takes priority over Referer when both present and origin matches
            (
                {"Origin": "https://medwiki.toolforge.org", "Referer": "https://medwiki.toolforge.org/path"},
                "https://medwiki.toolforge.org",
            ),
        ],
    )
    def test_allowed_domain_granted(self, app: Flask, headers: dict[str, str], expected) -> None:
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(headers=headers):
            from flask import request

            assert is_allowed(request) == expected

    @pytest.mark.parametrize(
        "headers",
        [
            # Subdomain of allowed domain — NOT allowed (exact match only)
            {"Origin": "https://sub.medwiki.toolforge.org"},
            # Superdomain — NOT allowed
            {"Origin": "https://toolforge.org"},
            # Completely different domain
            {"Origin": "https://evil.com"},
            # Subdomain spoofing attempt
            {"Origin": "https://medwiki.toolforge.org.evil.com"},
            # Both headers from untrusted domain
            {"Origin": "https://evil.com", "Referer": "https://evil.com/page"},
            # No headers at all
            {},
        ],
    )
    def test_not_allowed_domain_denied(self, app: Flask, headers: dict[str, str]) -> None:
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(headers=headers):
            from flask import request

            assert is_allowed(request) is None

    def test_referer_allowed_but_origin_denied(self, app: Flask) -> None:
        """
        Origin is untrusted but Referer is allowed.
        Current logic: iterates domains and checks both independently.
        Referer match → returns domain.
        """
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(
            headers={"Origin": "https://evil.com", "Referer": "https://medwiki.toolforge.org/page"}
        ):
            from flask import request

            result = is_allowed(request)
            assert result == "https://medwiki.toolforge.org"


# ------------------------------------------------------------------
# 3. CORS_DISABLED flag
# ------------------------------------------------------------------


class TestCorsDisabled:
    def test_disabled_with_origin_returns_origin(self, app: Flask) -> None:
        app.config["CORS_DISABLED"] = True
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(headers={"Origin": "https://unknown.com"}):
            from flask import request

            assert is_allowed(request) == "https://unknown.com"

    def test_disabled_without_origin_returns_wildcard(self, app: Flask) -> None:
        app.config["CORS_DISABLED"] = True
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(headers={}):
            from flask import request

            assert is_allowed(request) == "*"

    def test_disabled_bypasses_denied_domain(self, app: Flask) -> None:
        """Even a normally-denied domain passes when CORS_DISABLED."""
        app.config["CORS_DISABLED"] = True
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(headers={"Origin": "https://evil.com"}):
            from flask import request

            assert is_allowed(request) == "https://evil.com"


# ------------------------------------------------------------------
# 4. Edge cases
# ------------------------------------------------------------------


class TestEdgeCases:
    def test_malformed_origin_denied(self, app: Flask) -> None:
        """Malformed URL → get_host returns '' → denied."""
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(headers={"Origin": "not-a-valid-url"}):
            from flask import request

            assert is_allowed(request) is None

    def test_malformed_referer_denied(self, app: Flask) -> None:
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(headers={"Referer": ":::bad-url"}):
            from flask import request

            assert is_allowed(request) is None

    def test_empty_origin_header(self, app: Flask) -> None:
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(headers={"Origin": ""}):
            from flask import request

            assert is_allowed(request) is None

    def test_origin_with_port_not_in_allowed(self, app: Flask) -> None:
        """medwiki.toolforge.org:8080 ≠ medwiki.toolforge.org → denied."""
        from src.new_app.shared.cors.is_allowed_checker import is_allowed

        with app.test_request_context(headers={"Origin": "https://medwiki.toolforge.org:8080"}):
            from flask import request

            assert is_allowed(request) is None
