"""Unit tests for crypto module.

Tests for encryption/decryption helpers used for OAuth token storage.
"""

from __future__ import annotations

import pytest
from src.app_main.crypto import _require_fernet, decrypt_value, encrypt_value


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
        original = "héllo wörld 日本語"
        encrypted = encrypt_value(original)

        assert isinstance(encrypted, bytes)
        # Should be able to decrypt back
        decrypted = decrypt_value(encrypted)
        assert decrypted == original

    def test_encrypts_empty_string(self):
        """Test that empty string can be encrypted."""
        original = ""
        encrypted = encrypt_value(original)

        assert isinstance(encrypted, bytes)
        decrypted = decrypt_value(encrypted)
        assert decrypted == original

    def test_produces_different_tokens_for_same_input(self):
        """Test that encrypting same value produces different tokens (due to timestamp)."""
        original = "test_value"
        encrypted1 = encrypt_value(original)
        encrypted2 = encrypt_value(original)

        # Tokens should be different due to timestamp
        assert encrypted1 != encrypted2
        # But both should decrypt to same value
        assert decrypt_value(encrypted1) == decrypt_value(encrypted2) == original


class TestDecryptValue:
    """Tests for decrypt_value function."""

    def test_decrypts_to_original_value(self):
        """Test that decryption returns original value."""
        original = "my_secret_token"
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)

        assert decrypted == original

    def test_decrypts_unicode(self):
        """Test decryption of unicode strings."""
        original = "héllo wörld 🎉"
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)

        assert decrypted == original

    def test_raises_on_invalid_token(self):
        """Test that invalid token raises ValueError."""
        invalid_token = b"invalid_token_bytes"

        with pytest.raises(ValueError, match="Unable to decrypt stored token"):
            decrypt_value(invalid_token)

    def test_raises_on_tampered_token(self):
        """Test that tampered token raises ValueError."""
        original = "test_value"
        encrypted = encrypt_value(original)

        # Tamper with the token
        tampered = encrypted[:-5] + b"xxxxx"

        with pytest.raises(ValueError, match="Unable to decrypt stored token"):
            decrypt_value(tampered)

    def test_raises_on_empty_bytes(self):
        """Test that empty bytes raises ValueError."""
        with pytest.raises(ValueError, match="Unable to decrypt stored token"):
            decrypt_value(b"")


class TestRequireFernet:
    """Tests for _require_fernet function."""

    def test_returns_same_fernet_instance(self):
        """Test that same Fernet instance is returned on multiple calls."""
        fernet1 = _require_fernet()
        fernet2 = _require_fernet()

        assert fernet1 is fernet2

    def test_fernet_can_encrypt_and_decrypt(self):
        """Test that returned Fernet instance works correctly."""
        fernet = _require_fernet()
        original = "test_message"

        encrypted = fernet.encrypt(original.encode())
        decrypted = fernet.decrypt(encrypted).decode()

        assert decrypted == original


class TestRoundTrip:
    """Tests for encrypt/decrypt round-trip scenarios."""

    @pytest.mark.parametrize(
        "original",
        [
            "simple_string",
            "string_with_special_chars!@#$%",
            "unicode_日本語",
            "long_string_" * 100,
            "",
            "single_token_with_underscores_and-dashes123",
        ],
    )
    def test_various_strings_round_trip(self, original):
        """Test that various string types round-trip correctly."""
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        assert decrypted == original

    def test_oauth_token_like_values(self):
        """Test with values that resemble OAuth tokens."""
        # Simulate OAuth access token and secret
        access_token = "abcdefghijklmnop1234567890"
        access_secret = "secret_value_with_special_chars+/="

        encrypted_token = encrypt_value(access_token)
        encrypted_secret = encrypt_value(access_secret)

        assert decrypt_value(encrypted_token) == access_token
        assert decrypt_value(encrypted_secret) == access_secret
