"""
Tests for app_routes.cxtoken.cache module.
"""

import time

import pytest
from src.app_main.app_routes.cxtoken.cache import CxToken, get_from_store, store_jwt


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before each test."""
    from src.app_main.app_routes.cxtoken.cache import cache

    cache.clear()
    yield


class TestCxToken:
    """Tests for CxToken dataclass."""

    def test_creation_with_required_fields(self):
        """Test that CxToken can be created with required fields."""
        token = CxToken(age=3600, exp=1775879885, jwt="test_jwt_token")

        assert token.age == 3600
        assert token.exp == 1775879885
        assert token.jwt == "test_jwt_token"
        assert token.stored_at is not None

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
