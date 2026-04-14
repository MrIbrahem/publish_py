"""Tests for cors module."""

from unittest.mock import MagicMock

import pytest

from src.app_main.cors.cors import get_host


class TestGetHost:
    def test_with_scheme_and_port(self):
        assert get_host("https://example.com:8080/path") == "example.com:8080"

    def test_with_scheme_no_port(self):
        assert get_host("https://example.com/path") == "example.com"

    def test_with_port_only(sels):
        assert get_host("http://localhost:5000") == "localhost:5000"

    def test_domain_only(self):
        assert get_host("http://example.com") == "example.com"

    def test_empty_string(self):
        assert get_host("") == ""

    def test_with_query_and_port_and_fragment(self):
        assert get_host("https://example.com:8080/path?query=1#frag") == "example.com:8080"

    def test_with_query_and_fragment(self):
        assert get_host("https://example.com/p?q=1#frag") == "example.com"

    def test_https(self):
        assert get_host("https://api.example.org") == "api.example.org"

    def test_subdomain(self):
        assert get_host("http://www.example.com") == "www.example.com"

    def test_standard_https_url(self):
        assert get_host("https://example.com/path") == "example.com"

    def test_standard_http_url(self):
        assert get_host("http://example.com") == "example.com"

    def test_with_port(self):
        assert get_host("https://example.com:8080/path") == "example.com:8080"

    def test_with_subdomain(self):
        assert get_host("https://api.example.com/v1") == "api.example.com"

    def test_ip_address(self):
        assert get_host("http://192.168.1.1:9000/admin") == "192.168.1.1:9000"

    def test_no_scheme_returns_empty(self):
        # urlparse requires a scheme to identify netloc
        assert get_host("example.com/path") == ""

    def test_empty_string_returns_empty(self):
        assert get_host("") == ""

    def test_with_userinfo(self):
        assert get_host("https://user:pass@example.com") == "user:pass@example.com"
