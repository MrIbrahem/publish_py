"""Symmetric encryption helpers for storing OAuth secrets."""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from ...config import settings


class CryptoService:
    """Symmetric encryption using Fernet.

    The encryption key must be passed in at construction time
    (sourced from the TOKEN_ENCRYPTION_KEY environment variable).
    """

    def __init__(self) -> None:
        if not settings.oauth or not settings.oauth.encryption_key:
            raise RuntimeError("OAUTH_ENCRYPTION_KEY must be configured before using the crypto helpers")

        enc_key = settings.oauth.encryption_key
        key_bytes = enc_key.encode() if isinstance(enc_key, str) else enc_key
        self._fernet = Fernet(key_bytes)

    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt a UTF-8 string and return the raw Fernet token bytes."""
        return self._fernet.encrypt(plaintext.encode("utf-8"))

    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypt a Fernet token and return the UTF-8 string contents."""

        try:
            decrypted = self._fernet.decrypt(ciphertext)
        except InvalidToken as exc:
            raise ValueError("Unable to decrypt stored token") from exc
        return decrypted.decode("utf-8")

    def generate_key(self) -> str:
        """Utility: generate a new Fernet key."""
        return Fernet.generate_key().decode("utf-8")

    def _encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string and return the ciphertext as a string."""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def _decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string back to plaintext."""
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Failed to decrypt — invalid token or wrong key") from exc


def encrypt_value(ciphertext: str) -> bytes:
    return CryptoService().encrypt(ciphertext)


def decrypt_value(token: bytes) -> str:
    return CryptoService().decrypt(token)


__all__ = [
    "CryptoService",
    "encrypt_value",
    "decrypt_value",
]
