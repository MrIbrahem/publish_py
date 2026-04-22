"""Unit tests for crypto module.

Tests for encryption/decryption helpers used for OAuth token storage.
"""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet
from src.sqlalchemy_app.shared.core.crypto import _require_fernet, decrypt_value, encrypt_value


class TestEncryptValue:
    """Tests for encrypt_value function."""

    def test_encrypts_string_to_bytes(self) -> None:
        """Test that a string is encrypted to bytes."""
        original: str = "test_secret_value"
        encrypted: bytes = encrypt_value(original)

        assert isinstance(encrypted, bytes)
        assert encrypted != original.encode()

    def test_encrypts_unicode_string(self) -> None:
        """Test that unicode strings are handled correctly."""
        original: str = "héllo wörld 日本語"
        encrypted: bytes = encrypt_value(original)

        assert isinstance(encrypted, bytes)
        # Should be able to decrypt back
        decrypted: str = decrypt_value(encrypted)
        assert decrypted == original

    def test_encrypts_empty_string(self) -> None:
        """Test that empty string can be encrypted."""
        original: str = ""
        encrypted: bytes = encrypt_value(original)

        assert isinstance(encrypted, bytes)
        decrypted: str = decrypt_value(encrypted)
        assert decrypted == original

    def test_produces_different_tokens_for_same_input(self) -> None:
        """Test that encrypting same value produces different tokens (due to timestamp)."""
        original: str = "test_value"
        encrypted1: bytes = encrypt_value(original)
        encrypted2: bytes = encrypt_value(original)

        # Tokens should be different due to timestamp
        assert encrypted1 != encrypted2
        # But both should decrypt to same value
        assert decrypt_value(encrypted1) == decrypt_value(encrypted2) == original


class TestDecryptValue:
    """Tests for decrypt_value function."""

    def test_decrypts_to_original_value(self) -> None:
        """Test that decryption returns original value."""
        original: str = "my_secret_token"
        encrypted: bytes = encrypt_value(original)
        decrypted: str = decrypt_value(encrypted)

        assert decrypted == original

    def test_decrypts_unicode(self) -> None:
        """Test decryption of unicode strings."""
        original: str = "héllo wörld 🎉"
        encrypted: bytes = encrypt_value(original)
        decrypted: str = decrypt_value(encrypted)

        assert decrypted == original

    def test_raises_on_invalid_token(self) -> None:
        """Test that invalid token raises ValueError."""
        invalid_token: bytes = b"invalid_token_bytes"

        with pytest.raises(ValueError, match="Unable to decrypt stored token"):
            decrypt_value(invalid_token)

    def test_raises_on_tampered_token(self) -> None:
        """Test that tampered token raises ValueError."""
        original: str = "test_value"
        encrypted: bytes = encrypt_value(original)

        # Tamper with the token
        tampered: bytes = encrypted[:-5] + b"xxxxx"

        with pytest.raises(ValueError, match="Unable to decrypt stored token"):
            decrypt_value(tampered)

    def test_raises_on_empty_bytes(self) -> None:
        """Test that empty bytes raises ValueError."""
        with pytest.raises(ValueError, match="Unable to decrypt stored token"):
            decrypt_value(b"")


class TestRequireFernet:
    """Tests for _require_fernet function."""

    def test_returns_same_fernet_instance(self) -> None:
        """Test that same Fernet instance is returned on multiple calls."""
        fernet1: Fernet = _require_fernet()
        fernet2: Fernet = _require_fernet()

        assert fernet1 is fernet2

    def test_fernet_can_encrypt_and_decrypt(self) -> None:
        """Test that returned Fernet instance works correctly."""
        fernet: Fernet = _require_fernet()
        original: str = "test_message"

        encrypted: bytes = fernet.encrypt(original.encode())
        decrypted: str = fernet.decrypt(encrypted).decode()

        assert decrypted == original


class TestRoundTrip:
    """Tests for encrypt/decrypt round-trip scenarios."""

    @pytest.mark.parametrize(
        "original",
        [
            "simple_string",
            "string_with_special_chars!@#$%",
            "unicode_日本語",
            "long_string_" * 10,
            "",
            "single_token_with_underscores_and-dashes123",
        ],
    )
    def test_various_strings_round_trip(self, original: str) -> None:
        """Test that various string types round-trip correctly."""
        encrypted: bytes = encrypt_value(original)
        decrypted: str = decrypt_value(encrypted)
        assert decrypted == original

    def test_oauth_token_like_values(self) -> None:
        """Test with values that resemble OAuth tokens."""
        # Simulate OAuth access token and secret
        access_token: str = "abcdefghijklmnop1234567890"  # noqa: S105
        access_secret: str = "secret_value_with_special_chars+/="  # noqa: S105

        encrypted_token: bytes = encrypt_value(access_token)
        encrypted_secret: bytes = encrypt_value(access_secret)

        assert decrypt_value(encrypted_token) == access_token
        assert decrypt_value(encrypted_secret) == access_secret
