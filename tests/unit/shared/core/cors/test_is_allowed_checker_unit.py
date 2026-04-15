"""Tests for is_allowed_checker module."""

from unittest.mock import MagicMock

import pytest
from src.app_main.shared.core.cors.is_allowed_checker import get_host


class TestGetHost:
    @pytest.mark.parametrize(
        "url, expected",
        [
            pytest.param("https://example.com:8080/path", "example.com:8080", id="scheme_and_port"),
            pytest.param("https://example.com/path", "example.com", id="scheme_no_port"),
            pytest.param("http://localhost:5000", "localhost:5000", id="port_only"),
            pytest.param("https://example.com:8080/p?q=1#frag", "example.com:8080", id="query_and_port_and_fragment"),
            pytest.param("https://example.com/p?q=1#frag", "example.com", id="query_and_fragment"),
            pytest.param("http://www.example.com", "www.example.com", id="subdomain_www"),
            pytest.param("https://api.example.com/v1", "api.example.com", id="subdomain_api"),
            pytest.param("http://192.168.1.1:9000/admin", "192.168.1.1:9000", id="ip_address"),
            pytest.param("example.com/path", "", id="no_scheme_returns_empty"),
            pytest.param("", "", id="empty_string"),
            pytest.param("not-a-url", "", id="not-a-url"),
            pytest.param("sip://user:pass@example.com", "user:pass@example.com", id="userinfo"),
            pytest.param("ftp://ar.wikipedia.org", "ar.wikipedia.org", id="ar.wikipedia.org"),
        ],
    )
    def test_get_host(self, url, expected):
        assert get_host(url) == expected
