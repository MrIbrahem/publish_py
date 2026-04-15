"""Unit tests for cxtoken.cache module.

Tests for Content Translation token cache.
"""

import time
from unittest.mock import patch

import pytest

from src.app_main.app_routes.cxtoken.cache import (
    CxToken,
    cache,
    get_from_store,
    store_jwt,
)


@pytest.fixture
def clear_cache_fixture():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


class TestCxToken:
    """Tests for CxToken dataclass."""

    def test_create_with_required_fields(self):
        """Test creating CxToken with required fields."""
        token = CxToken(age=3600, exp=1234567890, jwt="test_jwt_token")

        assert token.age == 3600
        assert token.exp == 1234567890
        assert token.jwt == "test_jwt_token"
        assert token.stored_at > 0

    def test_to_dict_returns_correct_structure(self):
        """Test that to_dict returns correct dictionary structure."""
        token = CxToken(age=3600, exp=1234567890, jwt="test_jwt")

        result = token.to_dict()

        assert "age" in result
        assert "exp" in result
        assert "jwt" in result
        assert result["exp"] == 1234567890
        assert result["jwt"] == "test_jwt"


class TestStoreJwt:
    """Tests for store_jwt function."""

    def test_stores_valid_token(self, clear_cache_fixture):
        """Test that valid JWT token is stored correctly."""
        cxtoken = {"age": 3600, "exp": 1234567890, "jwt": "test_jwt"}

        store_jwt(cxtoken, "TestUser", "arwiki")

        assert ("TestUser", "arwiki") in cache

    def test_does_not_store_missing_jwt(self, clear_cache_fixture):
        """Test that token without JWT is not stored."""
        cxtoken = {"age": 3600, "exp": 1234567890}  # Missing jwt

        store_jwt(cxtoken, "TestUser", "arwiki")

        assert ("TestUser", "arwiki") not in cache

    def test_does_not_store_missing_age(self, clear_cache_fixture):
        """Test that token without age is not stored."""
        cxtoken = {"jwt": "test_jwt", "exp": 1234567890}  # Missing age

        store_jwt(cxtoken, "TestUser", "arwiki")

        assert ("TestUser", "arwiki") not in cache


class TestGetFromStore:
    """Tests for get_from_store function."""

    def test_returns_token_when_found(self, clear_cache_fixture):
        """Test that token is returned when found in cache."""
        cxtoken = {"age": 3600, "exp": 1234567890, "jwt": "test_jwt"}
        store_jwt(cxtoken, "TestUser", "arwiki")

        result = get_from_store("TestUser", "arwiki")

        assert result is not None
        assert result["jwt"] == "test_jwt"
        assert result["exp"] == 1234567890

    def test_returns_none_when_not_found(self, clear_cache_fixture):
        """Test that None is returned when token not in cache."""
        result = get_from_store("NonExistentUser", "arwiki")

        assert result is None
