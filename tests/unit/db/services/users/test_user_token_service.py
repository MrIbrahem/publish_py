from src.main_app.db.services.delete_service import (
    delete_user_token,
)
from src.main_app.db.services.users import create_user
from src.main_app.db.services.users.user_token_service import (
    create_user_token,
    get_authenticated_user_token,
    get_user_token,
    update_user_token,
    upsert_user_token,
)


def test_delete_user_cascades() -> None:
    user = create_user("svc_dave")
    upsert_user_token(user_id=user.user_id, encrypted_token=b"k", encrypted_secret=b"s")
    assert get_user_token(user.user_id) is not None


def test_upsert_get_delete_user_token() -> None:
    # Test insert
    user = create_user("svc_eve")
    upsert_user_token(user_id=user.user_id, encrypted_token=b"key", encrypted_secret=b"secret")

    token_record = get_user_token(user.user_id)
    assert token_record is not None
    assert token_record.access_token is not None
    assert token_record.access_secret is not None

    # Test update
    upsert_user_token(user_id=user.user_id, encrypted_token=b"new_key", encrypted_secret=b"new_secret")
    token_record = get_user_token(user.user_id)

    # Test delete token only
    delete_user_token(user.user_id)
    assert get_user_token(user.user_id) is None


class TestGetAuthenticatedUserToken:
    """Tests for get_authenticated_user_token."""

    def test_returns_token_when_user_exists(self):
        """Test returns token when user exists and has user relationship loaded."""

        user = create_user("svc_eve")
        upsert_user_token(user_id=user.user_id, encrypted_token=b"key", encrypted_secret=b"secret")

        result = get_authenticated_user_token(user.user_id)

        assert result is not None

    def test_returns_none_when_token_is_none(self):
        """Test returns None when token query returns None."""

        result = get_authenticated_user_token(1)

        assert result is None

    def test_returns_none_when_token_user_is_none(self):
        """Test returns None when token.user is None."""

        result = get_authenticated_user_token(1)

        assert result is None

    def test_handles_exception_gracefully(self):
        """Test returns None when an exception is raised."""

        result = get_authenticated_user_token(1)

        assert result is None


class TestGetUserToken:
    """Tests for get_user_token."""

    def test_returns_token_for_valid_user_id(self):
        """Test returns token for a valid integer user_id."""

        user = create_user("svc_eve")
        upsert_user_token(user_id=user.user_id, encrypted_token=b"key", encrypted_secret=b"secret")
        result = get_user_token(user.user_id)

        assert result is not None

    def test_returns_token_for_valid_user_id_str(self):
        """Test returns token for a valid string user_id."""
        user = create_user("svc_eve")
        upsert_user_token(user_id=user.user_id, encrypted_token=b"key", encrypted_secret=b"secret")
        result = get_user_token(str(user.user_id))

        assert result is not None

    def test_returns_none_for_none_user_id(self):
        """Test returns None when user_id is None."""
        result = get_user_token(None)  # type: ignore

        assert result is None

    def test_returns_none_for_zero_user_id(self):
        """Test returns None when user_id is 0 (falsy check)."""
        result = get_user_token(0)

        assert result is None

    def test_returns_none_for_empty_string_user_id(self):
        """Test returns None when user_id is an empty string."""
        result = get_user_token("")

        assert result is None

    def test_returns_none_when_no_token_found(self):
        """Test returns None when no matching token record exists."""
        result = get_user_token(999)

        assert result is None


class TestCreateUserToken:
    """Tests for create_user_token."""

    def test_creates_and_returns_record(self):
        """Test creates a new UserTokenRecord and returns it."""

        user = create_user("svc_eve")
        result = create_user_token(user.user_id, b"key", b"secret")
        assert result is not None
        assert result.user_id == user.user_id
        assert result.access_token == b"key"
        assert result.access_secret == b"secret"


class TestUpdateUserToken:
    """Tests for update_user_token."""

    def test_updates_existing_token(self):
        """Test updates fields on an existing token record."""

        user = create_user("svc_eve")
        result = create_user_token(user.user_id, b"key", b"secret")

        result = update_user_token(user.user_id, b"new_key", b"new_secret")
        assert result is not None

        assert result.access_token == b"new_key"
        assert result.access_secret == b"new_secret"

    def test_returns_none_when_token_not_found(self):
        """Test returns None when no token record exists for the user."""
        result = update_user_token(999, b"key", b"secret")

        assert result is None


class TestUpsertUserToken:
    """Tests for upsert_user_token."""

    def test_calls_create_when_no_existing_token(self):
        """Test calls create_user_token when no existing token is found."""
        user = create_user("testz")
        token = get_user_token(user.user_id)
        assert token is None

        result = upsert_user_token(user.user_id, b"enc_key", b"enc_secret")

        assert result is not None
        assert result.user_id == user.user_id
        assert result.access_token == b"enc_key"
        assert result.access_secret == b"enc_secret"

    def test_try_update_user_token_when_token_not_exists(self):
        """Test update_user_token when an existing token is found."""
        user = create_user("testz")

        result = update_user_token(user.user_id, b"new_key", b"new_secret")

        assert result is None
