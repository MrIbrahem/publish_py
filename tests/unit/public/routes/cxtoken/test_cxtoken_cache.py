"""
Unit tests for cxtoken.cache module.

Tests for token cache.
"""

import time

import pytest
from src.sqlalchemy_app.public.routes.cxtoken.cache import (
    CxToken,
    get_from_store,
    store_jwt,
    cache,
)


@pytest.fixture(autouse=True)
def clear_cache_fixture():
    """Clear cache before and after each test."""
    from src.sqlalchemy_app.public.routes.cxtoken.cache import cache

    cache.clear()
    yield
    cache.clear()


class TestCxToken:
    """Tests for CxToken dataclass."""

    def test_creation_with_required_fields(self):
        """Test that CxToken can be created with required fields."""
        token = CxToken(age=3600, exp=1775879885, jwt="test_jwt_token")

        assert token.age == 3600
        assert token.exp == 1775879885
        assert token.jwt == "test_jwt_token"
        assert token.stored_at is not None

    def test_create_with_required_fields(self):
        """Test creating CxToken with required fields."""
        token = CxToken(age=3600, exp=1234567890, jwt="test_jwt_token")

        assert token.age == 3600
        assert token.exp == 1234567890
        assert token.jwt == "test_jwt_token"
        assert token.stored_at > 0

    def test_to_dict_returns_correct_format(self):
        """Test that to_dict returns the expected dictionary format."""
        token = CxToken(age=3600, exp=1775879885, jwt="test_jwt")
        result = token.to_dict()

        assert "age" in result
        assert "exp" in result
        assert "jwt" in result
        assert result["age"] <= 3600
        assert result["exp"] == 1775879885
        assert result["jwt"] == "test_jwt"

    def test_to_dict_returns_correct_structure(self):
        """Test that to_dict returns correct dictionary structure."""
        token = CxToken(age=3600, exp=1234567890, jwt="test_jwt")
        result = token.to_dict()

        assert "age" in result
        assert "exp" in result
        assert "jwt" in result
        assert result["exp"] == 1234567890
        assert result["jwt"] == "test_jwt"

    def test_to_dict_age_decreases_over_time(self):
        """Test that age decreases as time passes."""
        token = CxToken(age=3600, exp=1775879885, jwt="test")
        time.sleep(0.1)
        result = token.to_dict()

        assert result["age"] < 3600


class TestStoreJwt:
    """Tests for store_jwt function."""

    def test_stores_valid_cxtoken(self):
        """Test that valid cxtoken is stored in cache."""
        cxtoken = {"age": 3600, "exp": 1775879885, "jwt": "valid_jwt_token"}

        store_jwt(cxtoken, "test_user", "enwiki")

        result = get_from_store("test_user", "enwiki")
        assert result is not None
        assert result["jwt"] == "valid_jwt_token"

    def test_stores_valid_cxtoken_2(self):
        """Test that valid JWT token is stored correctly."""
        cxtoken = {"age": 3600, "exp": 1234567890, "jwt": "test_jwt"}

        store_jwt(cxtoken, "TestUser", "arwiki")

        assert ("TestUser", "arwiki") in cache

    def test_ignores_missing_jwt(self):
        """Test that cxtoken without jwt is ignored."""
        cxtoken = {"age": 3600, "exp": 1775879885}

        store_jwt(cxtoken, "test_user", "enwiki")

        result = get_from_store("test_user", "enwiki")
        assert result is None

    def test_ignores_missing_age(self):
        """Test that cxtoken without age is ignored."""
        cxtoken = {"exp": 1775879885, "jwt": "test_jwt"}

        store_jwt(cxtoken, "test_user", "enwiki")

        result = get_from_store("test_user", "enwiki")
        assert result is None

    def test_ignores_missing_exp(self):
        """Test that cxtoken without exp is ignored."""
        cxtoken = {"age": 3600, "jwt": "test_jwt"}

        store_jwt(cxtoken, "test_user", "enwiki")

        result = get_from_store("test_user", "enwiki")
        assert result is None

    def test_stores_multiple_users(self):
        """Test that multiple users can be stored separately."""
        store_jwt({"age": 3600, "exp": 123, "jwt": "jwt1"}, "user1", "enwiki")
        store_jwt({"age": 3600, "exp": 456, "jwt": "jwt2"}, "user2", "enwiki")

        result1 = get_from_store("user1", "enwiki")
        result2 = get_from_store("user2", "enwiki")

        assert result1["jwt"] == "jwt1"
        assert result2["jwt"] == "jwt2"

    def test_stores_multiple_wikis(self):
        """Test that same user can have tokens for different wikis."""
        store_jwt({"age": 3600, "exp": 123, "jwt": "jwt_en"}, "test_user", "enwiki")
        store_jwt({"age": 3600, "exp": 456, "jwt": "jwt_de"}, "test_user", "dewiki")

        result_en = get_from_store("test_user", "enwiki")
        result_de = get_from_store("test_user", "dewiki")

        assert result_en["jwt"] == "jwt_en"
        assert result_de["jwt"] == "jwt_de"

    def test_overwrites_existing_token(self):
        """Test that storing overwrites existing token."""
        store_jwt({"age": 3600, "exp": 123, "jwt": "old_jwt"}, "test_user", "enwiki")
        store_jwt({"age": 3600, "exp": 456, "jwt": "new_jwt"}, "test_user", "enwiki")

        result = get_from_store("test_user", "enwiki")
        assert result["jwt"] == "new_jwt"

    def test_does_not_store_missing_jwt(self):
        """Test that token without JWT is not stored."""
        cxtoken = {"age": 3600, "exp": 1234567890}  # Missing jwt

        store_jwt(cxtoken, "TestUser", "arwiki")

        assert ("TestUser", "arwiki") not in cache

    def test_does_not_store_missing_age(self):
        """Test that token without age is not stored."""
        cxtoken = {"jwt": "test_jwt", "exp": 1234567890}  # Missing age

        store_jwt(cxtoken, "TestUser", "arwiki")

        assert ("TestUser", "arwiki") not in cache


class TestGetFromStore:
    """Tests for get_from_store function."""

    def test_returns_none_for_nonexistent_user(self):
        """Test that None is returned for user not in cache."""
        result = get_from_store("nonexistent_user", "enwiki")
        assert result is None

    def test_returns_none_for_nonexistent_wiki(self):
        """Test that None is returned for wiki not in cache."""
        store_jwt({"age": 3600, "exp": 123, "jwt": "test"}, "test_user", "enwiki")

        result = get_from_store("test_user", "dewiki")
        assert result is None

    def test_returns_token_with_remaining_age(self):
        """Test that returned token has remaining age calculated."""
        store_jwt({"age": 3600, "exp": 1775879885, "jwt": "test_jwt"}, "test_user", "enwiki")

        result = get_from_store("test_user", "enwiki")

        assert result is not None
        assert "age" in result
        assert result["age"] <= 3600

    def test_returns_exp_and_jwt(self):
        """Test that returned token contains exp and jwt."""
        store_jwt({"age": 3600, "exp": 1775879885, "jwt": "test_jwt"}, "test_user", "enwiki")

        result = get_from_store("test_user", "enwiki")

        assert result["exp"] == 1775879885
        assert result["jwt"] == "test_jwt"

    def test_returns_token_when_found(self):
        """Test that token is returned when found in cache."""
        cxtoken = {"age": 3600, "exp": 1234567890, "jwt": "test_jwt"}
        store_jwt(cxtoken, "TestUser", "arwiki")

        result = get_from_store("TestUser", "arwiki")

        assert result is not None
        assert result["jwt"] == "test_jwt"
        assert result["exp"] == 1234567890

    def test_returns_none_when_not_found(self):
        """Test that None is returned when token not in cache."""
        result = get_from_store("NonExistentUser", "arwiki")

        assert result is None
